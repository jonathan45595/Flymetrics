import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Searching in frontend/index.html:")
with open(r'c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\frontend\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'login' in line.lower() or 'modal' in line.lower():
        if 'onclick' in line.lower() or 'button' in line.lower():
            print(f"{i}: {line.strip()[:120]}")

print("\nSearching in frontend/js/app.js:")
with open(r'c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\frontend\js\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'login' in line.lower() or 'modal' in line.lower():
        if 'function' in line.lower() or 'display' in line.lower() or 'show' in line.lower() or 'style' in line.lower():
            print(f"{i}: {line.strip()[:120]}")
