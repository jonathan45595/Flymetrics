with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "role-selector" in line or "login-role" in line or "role-option" in line:
        print(f"  Line {idx+1}: {line.strip()[:140]}")
