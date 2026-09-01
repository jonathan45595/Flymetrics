import requests
BASE = 'http://localhost:3000/api/v1'

users = [
    ('admin@flymetrics.co', 'admin123', 'admin'),
    ('tecnico@flymetrics.co', 'tecnico123', 'tecnico'),
    ('cliente.demo@flymetrics.co', 'cliente123', 'cliente'),
]

for email, pwd, label in users:
    r = requests.post(f'{BASE}/auth/login', data={'username': email, 'password': pwd})
    d = r.json()
    # form login devuelve access_token directo
    tk = d.get('access_token') or d.get('data', {}).get('token', '')
    me_rol = 'NO TOKEN'
    if tk:
        rm = requests.get(f'{BASE}/auth/me', headers={'Authorization': f'Bearer {tk}'})
        me_rol = rm.json().get('data', {}).get('rol', 'ERROR')
    status = 'OK' if tk else f'FAIL {r.status_code}'
    print(f'  {label}: {status} | rol={me_rol} | email={email}')

print()
print('Portal Admin URL: http://localhost:3000/staff.html')
print('Portal Tecnico:  http://localhost:3000/staff.html (login con tecnico@flymetrics.co)')
print('Portal Cliente:  http://localhost:3000/index.html')
