import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app
from app.infrastructure.database.session import get_db, SessionLocal
from app.infrastructure.database.models.models import UsuarioModel
from app.infrastructure.security.jwt_handler import create_access_token, hash_password

client = TestClient(app)

db = SessionLocal()
admin_user = db.query(UsuarioModel).filter(UsuarioModel.rol == "administrador").first()
if not admin_user:
    admin_user = UsuarioModel(
        email="admin_test@flymetrics.co",
        contraseña=hash_password("admin123456"),
        rol="administrador"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

token = create_access_token(data={"sub": admin_user.email, "role": "administrador", "id": admin_user.id_usuarios})
headers = {"Authorization": f"Bearer {token}"}

print("=== PROBANDO ENDPOINTS DE ADMINISTRADOR ===")

# 1. Test Admin Password Change
res = client.post("/api/v1/auth/change-password", headers=headers, json={"new_password": "newadminpassword123"})
print(f"POST /api/v1/auth/change-password: HTTP {res.status_code} -> {res.json().get('message')}")
assert res.status_code == 200

# 2. Test List Usuarios
res = client.get("/api/v1/admin/usuarios", headers=headers)
print(f"GET /api/v1/admin/usuarios: HTTP {res.status_code} -> {len(res.json().get('data', []))} usuarios")
assert res.status_code == 200

# 3. Test Drones with pilot
res = client.get("/api/v1/drones", headers=headers)
print(f"GET /api/v1/drones: HTTP {res.status_code} -> {len(res.json().get('data', []))} drones")
assert res.status_code == 200

# 4. Test Agenda sorting (Admin)
res = client.get("/api/v1/admin/agenda", headers=headers)
print(f"GET /api/v1/admin/agenda: HTTP {res.status_code} -> {len(res.json().get('data', []))} agendas")
assert res.status_code == 200

# 5. Test Servicios
res = client.get("/api/v1/servicios", headers=headers)
print(f"GET /api/v1/servicios: HTTP {res.status_code} -> {len(res.json().get('data', []))} servicios")
assert res.status_code == 200

# 6. Test Pagos / Recibos
res = client.get("/api/v1/pagos", headers=headers)
print(f"GET /api/v1/pagos: HTTP {res.status_code} -> {len(res.json().get('data', []))} pagos")
assert res.status_code == 200

# 7. Test Public 24h Contact / Quotation Form
payload_contacto = {
    "nombre": "Carlos Arango Hacendado",
    "telefono": "3119876543",
    "email": "carlos.arango@finca-la-esperanza.co",
    "tipo": "Cotización de Fumigación y Aspersión",
    "hectareas": 45.5,
    "cultivo": "Arroz Fedearroz 68",
    "ubicacion": "Espinal, Tolima",
    "mensaje": "Requiero fumigación aérea de 45 hectáreas para control de piricularia y fertilización foliar urgente."
}
res = client.post("/api/v1/contacto", json=payload_contacto)
print(f"POST /api/v1/contacto: HTTP {res.status_code} -> Ticket #{res.json().get('data', {}).get('id_ticket')}")
assert res.status_code == 201
id_ticket = res.json().get('data', {}).get('id_ticket')

# 8. Test List Contact Requests (Admin)
res = client.get("/api/v1/contacto/solicitudes", headers=headers)
solicitudes = res.json().get('data', [])
print(f"GET /api/v1/contacto/solicitudes: HTTP {res.status_code} -> {len(solicitudes)} solicitudes recibidas")
assert res.status_code == 200
assert any(s.get('id_pqr') == id_ticket for s in solicitudes)

# 9. Test Update Contact Request Status (Admin)
res = client.patch(f"/api/v1/contacto/solicitudes/{id_ticket}/estado", headers=headers, json={"estado": "Atendido"})
print(f"PATCH /api/v1/contacto/solicitudes/{id_ticket}/estado: HTTP {res.status_code} -> Estado: {res.json().get('data', {}).get('estado')}")
assert res.status_code == 200
assert res.json().get('data', {}).get('estado') == "Atendido"

print("\n✓ TODAS LAS PRUEBAS DE ENDPOINTS Y COTIZACIONES 24H PASARON CON ÉXITO")
