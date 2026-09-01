import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('fronen/cliente.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="blocking-verification-overlay"')
if idx != -1:
    print('Found overlay at index', idx)
    print(text[idx-50:idx+2500])
else:
    print('Overlay not found')
