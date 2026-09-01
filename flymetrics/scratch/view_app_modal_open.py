with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = 705
end = min(len(lines), 765)
for i in range(start, end):
    safe_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
    print(f"  {i+1}: {safe_line}")
