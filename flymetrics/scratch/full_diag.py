import requests, json

BASE = 'http://localhost:3000/api/v1'

def login(email, password):
    r = requests.post(f'{BASE}/auth/login', data={'username': email, 'password': password})
    if r.status_code == 200:
        return r.json().get('data', {}).get('access_token', '')
    print(f'  LOGIN FAIL {r.status_code}: {r.text[:200]}')
    return None

admin_tk = login('admin@flymetrics.co', 'admin123')
print(f'Admin token: {"OK" if admin_tk else "FAIL"}')

tech_tk = login('tecnico@flymetrics.co', 'tecnico123')
print(f'Tecnico token: {"OK" if tech_tk else "FAIL"}')

client_tk = login('cliente.demo@flymetrics.co', 'cliente123')
print(f'Cliente token: {"OK" if client_tk else "FAIL"}')

AH = {'Authorization': f'Bearer {admin_tk}', 'Content-Type': 'application/json'}
TH = {'Authorization': f'Bearer {tech_tk}', 'Content-Type': 'application/json'}
CH = {'Authorization': f'Bearer {client_tk}', 'Content-Type': 'application/json'} if client_tk else {}

print('\n--- GET ENDPOINTS ---')
endpoints = [
    ('/servicios', None),
    ('/drones', AH),
    ('/tecnicos', AH),
    ('/clientes', AH),
    ('/admin/agenda', AH),
    ('/admin/pagos', AH),
    ('/reportes-vuelo', AH),
    ('/admin/usuarios', AH),
    ('/fincas', CH),
    ('/tecnico/agenda', TH),
]
for path, headers in endpoints:
    r = requests.get(f'{BASE}{path}', headers=headers or {})
    d = r.json()
    data = d.get('data', [])
    count = len(data) if isinstance(data, list) else 'obj'
    status = 'OK' if r.status_code == 200 else f'ERROR {r.status_code}'
    msg = d.get('message', d.get('detail', ''))[:60] if r.status_code != 200 else ''
    print(f'  {status} {path} -> {count} items {msg}')

print('\n--- POST/CREATE TESTS ---')
# Test crear agenda turno (como admin simulando cliente)
if admin_tk:
    # Get existing finca + servicio IDs
    srv_r = requests.get(f'{BASE}/servicios')
    srvs = srv_r.json().get('data', [])
    finca_r = requests.get(f'{BASE}/fincas', headers=CH) if CH else None
    fincas = finca_r.json().get('data', []) if finca_r else []
    
    print(f'  Servicios disponibles: {[s.get("id_servicio") for s in srvs]}')
    print(f'  Fincas del cliente demo: {[f.get("id_finca") for f in fincas]}')
    
    if srvs and fincas:
        from datetime import date, timedelta
        payload = {
            'id_finca': fincas[0]['id_finca'],
            'id_servicio': srvs[0]['id_servicio'],
            'fecha_de_turno': str(date.today() + timedelta(days=5)),
            'hora_inicio_estimada': '09:00:00',
            'tipo_turno': 'Fumigacion'
        }
        r = requests.post(f'{BASE}/agenda', json=payload, headers=CH)
        print(f'  POST /agenda: {r.status_code} -> {r.text[:200]}')

# Test crear drone
if admin_tk:
    drone_payload = {'modelo': 'Test Drone API', 'tipo': 'aspersion', 'estado': 'disponible', 'numero_serie': 'TEST-999'}
    r = requests.post(f'{BASE}/drones', json=drone_payload, headers=AH)
    print(f'  POST /drones: {r.status_code} -> {r.text[:200]}')
    if r.status_code in (200, 201):
        new_id = r.json().get('data', {}).get('id_drone')
        if new_id:
            rd = requests.delete(f'{BASE}/drones/{new_id}', headers=AH)
            print(f'  DELETE /drones/{new_id}: {rd.status_code}')

# Test crear servicio
if admin_tk:
    srv_payload = {'nombre_servicio': 'Test Servicio API', 'descripcion': 'Test', 'precio_base_m2': 0.75}
    r = requests.post(f'{BASE}/servicios', json=srv_payload, headers=AH)
    print(f'  POST /servicios: {r.status_code} -> {r.text[:200]}')
    if r.status_code in (200, 201):
        new_id = r.json().get('data', {}).get('id_servicio')
        if new_id:
            rd = requests.delete(f'{BASE}/servicios/{new_id}', headers=AH)
            print(f'  DELETE /servicios/{new_id}: {rd.status_code}')

print('\nDONE')
