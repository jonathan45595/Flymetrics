import requests
BASE = 'http://localhost:3000/api/v1'

# Login admin
r = requests.post(f'{BASE}/auth/login', data={'username': 'admin@flymetrics.co', 'password': 'admin123'})
tk = r.json().get('access_token') or r.json().get('data', {}).get('token', '')
H = {'Authorization': f'Bearer {tk}', 'Content-Type': 'application/json'}

# Create a test técnico user
payload = {
    'email': 'new_tecnico_test@flymetrics.co',
    'contraseña': 'testpassword123',
    'rol': 'tecnico',
    'nombre': 'Técnico',
    'apellido_1': 'Prueba',
    'apellido_2': 'Dos',
    'telefono': '3109998877',
    'certificacion': 'Piloto RPAS Nivel A'
}

r_post = requests.post(f'{BASE}/tecnicos', json=payload, headers=H)
print("POST STATUS:", r_post.status_code)
print("POST RESPONSE:", r_post.json())
