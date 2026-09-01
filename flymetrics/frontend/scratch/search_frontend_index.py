import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\frontend\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("File size:", len(content))
lines = content.splitlines()

print("Searching for auth modal or login buttons:")
for i, line in enumerate(lines, 1):
    if 'modal' in line.lower() or 'auth' in line.lower() or 'acceder' in line.lower() or 'ingresar' in line.lower() or 'sesion' in line.lower() or 'sesión' in line.lower():
        if len(line.strip()) < 150:
            print(f"{i}: {line.strip()}")
        else:
            print(f"{i}: {line.strip()[:150]}...")
