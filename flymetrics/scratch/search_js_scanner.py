with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "proceedToScannerSetup" in line and "function" in line:
        print(f"=== Line {idx+1} ===")
        start = max(0, idx - 5)
        end = min(len(lines), idx + 60)
        for i in range(start, end):
            safe_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
            print(f"  {i+1}: {safe_line}")
        break
