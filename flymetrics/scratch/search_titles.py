with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if any(k in line for k in ["text-stroke", "stroke", "text-shadow", "border-bottom", "font-family", "h2", "h3", "hero-title"]):
        safe_line = line.strip()[:140].encode('ascii', errors='replace').decode('ascii')
        print(f"Line {idx+1}: {safe_line}")
