with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if ".json(" in line:
        safe_line = line.strip()[:140].encode('ascii', errors='replace').decode('ascii')
        print(f"Line {idx+1}: {safe_line}")
