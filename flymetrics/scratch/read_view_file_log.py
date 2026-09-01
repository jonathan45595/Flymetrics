import json
log_file = r"C:\Users\MIGUEL\.gemini\antigravity\brain\a1b7b92d-6c62-431b-8637-a8c31482da25\.system_generated\logs\transcript_full.jsonl"
with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in [214, 215, 222, 234, 235, 298, 299, 306, 329, 330]:
            print(f"--- Line {i} ---")
            try:
                data = json.loads(line)
                # print data keys
                print("Keys:", data.keys())
                # If there is content, print it
                if "content" in data:
                    print("Content length:", len(data["content"]))
                    print("Content preview:", data["content"][:200])
                if "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        print("Tool call args:", tc.get("args"))
            except Exception as e:
                print("Err:", e)
