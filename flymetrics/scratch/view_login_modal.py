with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1099, min(len(lines), 1140)):
    safe_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
    print(f"  {i+1}: {safe_line}")
