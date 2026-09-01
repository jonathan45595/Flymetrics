import requests
BASE = 'http://localhost:3000/api/v1'

# Login client
r_login = requests.post(f'{BASE}/auth/login', data={'username': 'cliente.demo@flymetrics.co', 'password': 'cliente123'})
d_login = r_login.json()
tk = d_login.get('access_token') or d_login.get('data', {}).get('token', '')
H = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# Get finca + service
fincas = requests.get(f'{BASE}/fincas', headers=H).json().get('data', [])
srvs = requests.get(f'{BASE}/servicios', headers=H).json().get('data', [])

print("Fincas:", fincas)
print("Servicios:", srvs)

if fincas and srvs:
    payload = {
        'id_finca': fincas[0]['id_finca'],
        'id_servicio': srvs[0]['id_servicio'],
        'fecha_de_turno': '2026-07-25',
        'hora_inicio_estimada': '08:00:00',
        'tipo_turno': 'Fumigación',
        'cel': '3001234567',
        'observaciones_servicio': 'Test API booking'
    }
    r = requests.post(f'{BASE}/agenda', json=payload, headers=H)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)
