import requests
BASE = 'http://localhost:3000/api/v1'

# Login admin
r = requests.post(f'{BASE}/auth/login', data={'username': 'admin@flymetrics.co', 'password': 'admin123'})
tk = r.json().get('access_token') or r.json().get('data', {}).get('token', '')
H = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# Get service 1
r_get = requests.get(f'{BASE}/servicios')
srvs = r_get.json().get('data', [])
print("Servicio antes:", srvs[0])

# Update service 1
payload = {
    'nombre_servicio': 'Fumigacion aerea (Modificada)',
    'descripcion': srvs[0]['descripcion'],
    'precio_base_m2': 0.85
}
r_put = requests.put(f'{BASE}/servicios/1', json=payload, headers=H)
print("PUT STATUS:", r_put.status_code)
print("PUT RESPONSE:", r_put.json())

# Check after
r_check = requests.get(f'{BASE}/servicios')
print("Servicio después:", r_check.json().get('data', [])[0])
