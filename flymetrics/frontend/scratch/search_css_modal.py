import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'modal' in line.lower() or 'open' in line.lower():
        print(f"{i}: {line.strip()}")
