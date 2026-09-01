import json
import os

log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"

print("Searching matches...")
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "style.css" in line:
                print(f"Line {i} contains style.css")
                try:
                    data = json.loads(line)
                    # Let's inspect keys
                    print("Keys:", data.keys())
                    if "tool_calls" in data:
                        print("Tool calls found!")
                        for tc in data["tool_calls"]:
                            print("Tool:", tc.get("name"))
                            print("Args keys:", tc.get("arguments", {}).keys())
                except Exception as e:
                    print("JSON decode err:", e)
