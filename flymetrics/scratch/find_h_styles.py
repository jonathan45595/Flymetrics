with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.finditer(r'([^\}\{]*h[1-3][^\}\{]*\{[^\}]*\})', content)
for m in matches:
    safe_txt = m.group(0).encode('ascii', errors='replace').decode('ascii')
    print(safe_txt)
