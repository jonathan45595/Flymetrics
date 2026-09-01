with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "const modal = document.getElementById('service-modal');" in line:
        print(f"=== Line {idx+1} ===")
        start = max(0, idx - 15)
        end = min(len(lines), idx + 60)
        for i in range(start, end):
            safe_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
            print(f"  {i+1}: {safe_line}")
        break
