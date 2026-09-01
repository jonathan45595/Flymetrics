import requests
BASE = 'http://localhost:3000/api/v1'

# Login as seeded client
r = requests.post(f'{BASE}/auth/login', data={'username': 'cliente.demo@flymetrics.co', 'password': 'cliente123'})
print("LOGIN STATUS:", r.status_code)
tk = r.json().get('access_token') or r.json().get('data', {}).get('token', '')
H = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# Get current client profile to find the real id_cliente
r_me = requests.get(f'{BASE}/clientes/me', headers=H)
client_id = r_me.json().get('data', {}).get('id_cliente') or r_me.json().get('id_cliente')
print("AUTHENTICATED CLIENT ID:", client_id)

# 1. List current fincas
r_list1 = requests.get(f'{BASE}/fincas', headers=H)
print("INITIAL FINCAS:", r_list1.json().get('data', []))

# 2. Create a new finca with the matching client ID
finca_payload = {
    'id_cliente': client_id,
    'nombre_finca': 'Finca Temporal para Borrar',
    'ubicacion_municipio': 'Yopal',
    'departamento': 'Casanare',
    'hectareas': 55.4,
    'latitud': 5.3378,
    'longitud': -72.3959
}
r_create = requests.post(f'{BASE}/fincas', json=finca_payload, headers=H)
print("CREATE STATUS:", r_create.status_code)
f_data = r_create.json().get('data', {})
f_id = f_data.get('id_finca')
print("CREATED FINCA ID:", f_id)

# 3. List fincas after creation
r_list2 = requests.get(f'{BASE}/fincas', headers=H)
print("FINCAS AFTER CREATE:", [f['id_finca'] for f in r_list2.json().get('data', [])])

# 4. Delete the finca
if f_id:
    r_delete = requests.delete(f'{BASE}/fincas/{f_id}', headers=H)
    print("DELETE STATUS:", r_delete.status_code)
    print("DELETE RESPONSE:", r_delete.json())

# 5. List fincas after delete
r_list3 = requests.get(f'{BASE}/fincas', headers=H)
print("FINCAS AFTER DELETE:", [f['id_finca'] for f in r_list3.json().get('data', [])])
