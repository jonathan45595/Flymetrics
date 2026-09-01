with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

line_numbers = [1903, 1966, 1980, 2004, 2024, 2027, 2328, 2545, 2699, 2835, 3745, 3915, 3934]
for ln in line_numbers:
    print(f"=== Line {ln} ===")
    start = max(0, ln - 6)
    end = min(len(lines), ln + 6)
    for idx in range(start, end):
        safe_line = lines[idx].strip().encode('ascii', errors='replace').decode('ascii')
        print(f"  {idx+1}: {safe_line}")
