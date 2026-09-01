import json
import os

log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"
style_css_path = r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\css\style.css"
old_style_css_path = r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\css\old_style.css"

print("Parsing transcript...")

style_css_content = ""
old_style_css_content = ""

if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                # Look for tool calls or results
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    args = tc.get("args", {})
                    # If it's a file write or edit
                    if "TargetFile" in args:
                        target = args["TargetFile"]
                        # Check style.css
                        if "style.css" in target and not target.endswith("admin.css"):
                            content = args.get("CodeContent") or args.get("ReplacementContent")
                            if content and len(content) > 100:
                                if "old_style" in target:
                                    old_style_css_content = content
                                else:
                                    style_css_content = content
            except Exception as e:
                pass

if style_css_content:
    print(f"Found style.css content ({len(style_css_content)} bytes). Restoring...")
    with open(style_css_path, "w", encoding="utf-8") as f:
        f.write(style_css_content)
else:
    print("Could not find style.css content in log.")

if old_style_css_content:
    print(f"Found old_style.css content ({len(old_style_css_content)} bytes). Restoring...")
    with open(old_style_css_path, "w", encoding="utf-8") as f:
        f.write(old_style_css_content)
else:
    print("Could not find old_style.css content in log.")
