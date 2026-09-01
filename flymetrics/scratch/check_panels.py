import re

with open('fronen/cliente.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('=== Nav items data-panel values ===')
nav_panels = re.findall(r'data-panel="([^"]+)"', text)
print(set(nav_panels))

print('\n=== Panel IDs in HTML ===')
panel_ids = re.findall(r'id="panel-([^"]+)"', text)
print(panel_ids)

print('\n=== Missing panels (defined in nav but no ID in HTML) ===')
for p in set(nav_panels):
    if p not in panel_ids:
        print(f'Missing panel: panel-{p}')
