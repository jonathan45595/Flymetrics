with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.finditer(r'<style[^>]*>([\s\S]*?)</style>', content)
for m in matches:
    print("=== Style Block ===")
    print(m.group(1).strip()[:300])
