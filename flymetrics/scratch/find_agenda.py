import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('fronen/cliente.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the new agenda modal
idx = text.find('agFecha')
if idx != -1:
    print(f'agFecha found at index {idx}')
    print(text[idx-3000:idx+200])
else:
    print('agFecha not found')
