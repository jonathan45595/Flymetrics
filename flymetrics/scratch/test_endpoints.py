import requests, json

BASE = 'http://localhost:3000/api/v1'

# Login admin
r = requests.post(f'{BASE}/auth/login', data={'username': 'admin@flymetrics.co', 'password': 'admin123'})
tk = r.json().get('data', {}).get('access_token', '')
H = {'Authorization': f'Bearer {tk}'}
print(f'Admin login: {r.status_code} {"OK" if tk else "FAIL"}')

# Test key endpoints  
tests = [
    ('GET', '/servicios', None),
    ('GET', '/drones', H),
    ('GET', '/tecnicos', H),
    ('GET', '/clientes', H),
    ('GET', '/admin/agenda', H),
    ('GET', '/admin/pagos', H),
    ('GET', '/reportes-vuelo', H),
    ('GET', '/admin/usuarios', H),
]
for method, path, headers in tests:
    r2 = requests.get(f'{BASE}{path}', headers=headers or {})
    d = r2.json().get('data', [])
    count = len(d) if isinstance(d, list) else 'obj'
    print(f'  {r2.status_code} {path} -> {count} items')

# Client login
r3 = requests.post(f'{BASE}/auth/login', data={'username': 'cliente.demo@flymetrics.co', 'password': 'cliente123'})
tk2 = r3.json().get('data', {}).get('access_token', '')
print(f'Client login: {r3.status_code} {"OK" if tk2 else "FAIL"}')
H2 = {'Authorization': f'Bearer {tk2}'}

rf = requests.get(f'{BASE}/fincas', headers=H2)
fincas = rf.json().get('data', [])
print(f'  {rf.status_code} /fincas (cliente) -> {len(fincas)} fincas')

# Tecnico login
r4 = requests.post(f'{BASE}/auth/login', data={'username': 'tecnico@flymetrics.co', 'password': 'tecnico123'})
tk3 = r4.json().get('data', {}).get('access_token', '')
print(f'Tecnico login: {r4.status_code} {"OK" if tk3 else "FAIL"}')
H3 = {'Authorization': f'Bearer {tk3}'}
rt = requests.get(f'{BASE}/tecnico/agenda', headers=H3)
print(f'  {rt.status_code} /tecnico/agenda -> {len(rt.json().get("data", []))} turnos')

print('\nDONE - All endpoints checked')
