import json
log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"
with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in [670, 672, 676]:
            print(f"--- Line {i} ---")
            data = json.loads(line)
            for tc in data.get("tool_calls", []):
                print("Tool:", tc.get("name"))
                print("Keys:", tc.keys())
                for k, v in tc.items():
                    if k != "arguments" and k != "args":
                        print(f"  {k}: {str(v)[:100]}")
                    else:
                        print(f"  {k} keys: {v.keys() if hasattr(v, 'keys') else 'not a dict'}")
                        # If it is a string (some APIs return arguments as a stringified JSON)
                        if isinstance(v, str):
                            try:
                                loaded = json.loads(v)
                                print(f"  {k} stringified keys: {loaded.keys()}")
                                if "TargetFile" in loaded:
                                    print(f"    TargetFile: {loaded['TargetFile']}")
                                    print(f"    Content length: {len(loaded.get('CodeContent', ''))}")
                            except Exception as e:
                                print("    Could not parse stringified args:", e)
