import json
import os
import re

log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"

steps_with_css = []
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "style.css" in line or "old_style.css" in line:
                steps_with_css.append((i, line))

# Now let's print detailed tool calls and contents
for idx, line_str in steps_with_css:
    try:
        data = json.loads(line_str)
        step = data.get("step_index")
        type_ = data.get("type")
        source = data.get("source")
        
        # If model request (contains tool calls)
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                args = tc.get("args", {})
                target = args.get("AbsolutePath", "")
                if "style.css" in target or "old_style.css" in target:
                    print(f"Step {step} (Line {idx}) - REQUEST - Tool: {tc.get('name')} - Target: {target} - Range: {args.get('StartLine')}-{args.get('EndLine')}")
        
        # If system/user response (contains content)
        if "content" in data and type_ == "PLANNER_RESPONSE": # Wait, tool results are type: TOOL_RESPONSE or similar
            pass
        elif "content" in data:
            # Let's check if it's the result of view_file
            content = data["content"]
            if "File Path:" in content and ("style.css" in content or "old_style.css" in content):
                # parse path and lines shown
                lines_match = re.search(r"Showing lines (\d+) to (\d+)", content)
                path_match = re.search(r"File Path: `file:///(.*?)`", content)
                path = path_match.group(1) if path_match else "unknown"
                range_str = lines_match.group(0) if lines_match else "all"
                print(f"Line {idx} - RESPONSE - Path: {path} - {range_str} - Content len: {len(content)}")
    except Exception as e:
        pass
