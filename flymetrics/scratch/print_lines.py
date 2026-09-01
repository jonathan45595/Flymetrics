import json
log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"
with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in [670, 672, 676]:
            print(f"--- Line {i} ---")
            data = json.loads(line)
            for tc in data.get("tool_calls", []):
                args = tc.get("args", {})
                print("Target:", args.get("TargetFile"))
                print("CodeContent starts with:", str(args.get("CodeContent"))[:100])
