with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "form-login" in line or "submit" in line:
        if "addEventListener" in line:
            print(f"=== Line {idx+1} ===")
            start = max(0, idx - 10)
            end = min(len(lines), idx + 50)
            for i in range(start, end):
                safe_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
                print(f"  {i+1}: {safe_line}")
            break
