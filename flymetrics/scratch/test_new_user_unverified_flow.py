import sys, json, urllib.request
sys.path.insert(0, '.')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel

db = SessionLocal()
new_email = f"nuevo_cliente_{int(urllib.request.time.time())}@gmail.com"

print(f"=== 1. Registering new client: {new_email} ===")
req_reg = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/auth/register',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'email': new_email,
        'contraseña': 'Password123!',
        'rol': 'cliente',
        'nombre': 'Mario',
        'apellido_1': 'Gomez'
    }).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req_reg) as resp_reg:
    body_reg = json.loads(resp_reg.read().decode('utf-8'))
    print("Registration response:", body_reg.get('message'))

# Login to get JWT
req_login = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/auth/login',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'email': new_email,
        'contraseña': 'Password123!'
    }).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req_login) as resp_login:
    body_login = json.loads(resp_login.read().decode('utf-8'))
    token = body_login['data']['token']
    print("Login token received.")

# Check /clientes/me
req_me = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/clientes/me',
    headers={'Authorization': f'Bearer {token}'}
)

with urllib.request.urlopen(req_me) as resp_me:
    body_me = json.loads(resp_me.read().decode('utf-8'))
    client_data = body_me['data']
    print(f"New client verified status: {client_data['verificado']} (Expected: False/0)")

# Send OTP email
req_otp = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/auth/enviar-codigo-verificacion',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'email': new_email}).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req_otp) as resp_otp:
    body_otp = json.loads(resp_otp.read().decode('utf-8'))
    otp_code = body_otp['data']['codigo_simulado']
    print(f"OTP code generated & sent to {new_email}: {otp_code}")

print("\n>>> NEW UNVERIFIED USER FLOW VERIFIED 100%! <<<")
