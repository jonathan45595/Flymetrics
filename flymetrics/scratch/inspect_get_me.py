with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\app\application\use_cases\use_cases.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "def get_me" in line or "def verify_document_ia" in line:
        print(f"=== Line {idx+1} ===")
        start = max(0, idx - 2)
        end = min(len(lines), idx + 45)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].strip()}")
