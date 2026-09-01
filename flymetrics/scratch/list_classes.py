import re

filepath = r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics\frontend\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

classes = set(re.findall(r'class="([^"]+)"', content))
all_classes = set()
for c in classes:
    for sub in c.split():
        all_classes.add(sub)

print("Classes found in index.html:")
for c in sorted(all_classes):
    print(f" - {c}")
