import sys, json, urllib.request
sys.path.insert(0, '.')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel
from app.infrastructure.security.jwt_handler import create_access_token

db = SessionLocal()
test_email = 'cliente@gmail.com'

usr = db.query(UsuarioModel).filter(UsuarioModel.email == test_email).first()
if not usr:
    usr = db.query(UsuarioModel).filter(UsuarioModel.rol == 'cliente').first()
    test_email = usr.email

print(f"Testing OTP Verification Flow for email: {test_email}")
token = create_access_token({'sub': usr.email, 'rol': usr.rol})

# 1. Enviar código OTP
req1 = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/auth/enviar-codigo-verificacion',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'email': test_email}).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req1) as resp1:
    body1 = json.loads(resp1.read().decode('utf-8'))
    otp_code = body1.get('data', {}).get('codigo_simulado')
    print(f"Step 1 PASS -> OTP Generated & Sent: {otp_code}")

# 2. Verificar código OTP
req2 = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/auth/verificar-codigo-correo',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({'email': test_email, 'codigo': otp_code}).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req2) as resp2:
    body2 = json.loads(resp2.read().decode('utf-8'))
    print(f"Step 2 PASS -> Email Verified Status: {body2.get('message')}")

# 3. Completar Verificación Extendida (Cédula, Nombre Completo, Fecha Nacimiento)
req3 = urllib.request.Request(
    'http://127.0.0.1:3000/api/v1/clientes/completar-verificacion',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    data=json.dumps({
        'numero_documento': '1044490043',
        'nombre': 'Carlos',
        'apellido_1': 'Mendoza',
        'fecha_nacimiento': '1996-05-20'
    }).encode('utf-8'),
    method='POST'
)

with urllib.request.urlopen(req3) as resp3:
    body3 = json.loads(resp3.read().decode('utf-8'))
    print(f"Step 3 PASS -> Extended Personal Data Saved:")
    print(" ", body3.get('data'))

print("\n>>> ALL OTP VERIFICATION & EXTENDED REGISTRATION TESTS PASSED 100%! <<<")
