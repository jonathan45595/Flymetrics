import os, sys, urllib.request, json
sys.path.insert(0, '.')

print("==================================================")
print("     FLYMETRICS SYSTEM AUDIT & HEALTH CHECK       ")
print("==================================================")

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, FincaModel, AgendaModel, ServicioModel
from app.infrastructure.security.jwt_handler import create_access_token

db = SessionLocal()

print(f"[OK] Database connection active")
print(f"[OK] Total Users: {db.query(UsuarioModel).count()}")
print(f"[OK] Total Fincas: {db.query(FincaModel).count()}")
print(f"[OK] Total Agendas: {db.query(AgendaModel).count()}")
print(f"[OK] Total Servicios: {db.query(ServicioModel).count()}")

admin_usr = db.query(UsuarioModel).filter(UsuarioModel.email == 'admin@flymetrics.co').first()
cli_usr = db.query(UsuarioModel).filter(UsuarioModel.rol == 'cliente').first()

admin_token = create_access_token({'sub': admin_usr.email, 'rol': admin_usr.rol}) if admin_usr else ''
cli_token = create_access_token({'sub': cli_usr.email, 'rol': cli_usr.rol}) if cli_usr else ''

endpoints = [
    ('GET', '/api/v1/servicios', None, 'Servicios Catalogo'),
    ('GET', '/api/v1/fincas', cli_token, 'Mis Fincas Cliente'),
    ('GET', '/api/v1/agenda/mis-turnos', cli_token, 'Mis Turnos Cliente'),
    ('GET', '/api/v1/pagos/mis-pagos', cli_token, 'Mis Pagos Cliente'),
    ('GET', '/api/v1/entregables/mis-archivos', cli_token, 'Mis Entregables Cliente'),
    ('GET', '/api/v1/pqrs', cli_token, 'PQRS Cliente'),
    ('GET', '/api/v1/admin/usuarios', admin_token, 'Admin usuarios'),
    ('GET', '/api/v1/admin/agenda', admin_token, 'Admin Agenda'),
    ('GET', '/api/v1/clientes', admin_token, 'Admin Clientes'),
    ('GET', '/api/v1/tecnicos', admin_token, 'Admin Tecnicos'),
    ('GET', '/api/v1/drones', admin_token, 'Admin Drones'),
]

print("\n--- Endpoints Check ---")
all_ok = True
for method, path, token, label in endpoints:
    url = f"http://127.0.0.1:3000{path}"
    headers = {}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cnt = len(data.get('data', [])) if isinstance(data, dict) and isinstance(data.get('data'), list) else 'OK'
            print(f" [PASS] {label:<22} -> HTTP {resp.status} (Records: {cnt})")
    except Exception as e:
        all_ok = False
        print(f" [FAIL] {label:<22} -> ERROR: {e}")

print("==================================================")
if all_ok:
    print(" >>> RESULT: ALL SYSTEMS 100% OPERATIONAL & READY! <<<")
print("==================================================")
