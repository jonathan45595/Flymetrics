import requests
BASE = 'http://localhost:3000/api/v1'

# Login client
r = requests.post(f'{BASE}/auth/login', data={'username': 'carlos@email.com', 'password': 'password123'})
tk = r.json().get('access_token') or r.json().get('data', {}).get('token', '')
H = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# Create a test finca
finca_payload = {
    'id_cliente': 1,
    'nombre_finca': 'Finca Test Delete',
    'ubicacion_municipio': 'Bogota',
    'departamento': 'Cundinamarca',
    'hectareas': 12.5,
    'latitud': 4.6097,
    'longitud': -74.0721
}
r_create = requests.post(f'{BASE}/fincas', json=finca_payload, headers=H)
print("CREATE STATUS:", r_create.status_code)
f_data = r_create.json().get('data', {})
f_id = f_data.get('id_finca')
print("CREATED FINCA ID:", f_id)

if f_id:
    # Delete test finca
    r_delete = requests.delete(f'{BASE}/fincas/{f_id}', headers=H)
    print("DELETE STATUS:", r_delete.status_code)
    print("DELETE RESPONSE:", r_delete.json())
