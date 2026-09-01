import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r'C:\Users\migue\.gemini\antigravity-ide\brain\a8f93277-30bd-4e9c-bcc8-ac9e5808eb07\.system_generated\logs\transcript.jsonl'

user_msgs = []
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            user_msgs.append((data.get('step_index'), data.get('content', '')))

print(f"Total user messages: {len(user_msgs)}")
for step, content in user_msgs[-25:]:
    print(f"\n================ STEP {step} ================")
    print(content)
