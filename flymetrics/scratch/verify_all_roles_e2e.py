import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient  # type: ignore

from main import app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel, TecnicoModel
from app.infrastructure.security.jwt_handler import hash_password

client = TestClient(app)
db = SessionLocal()

print("=== VERIFICACIÓN Y PRUEBA E2E COMPLETA DE ROLES (ADMIN, TÉCNICO, CLIENTE) ===")

def ensure_users():
    # Admin
    admin = db.query(UsuarioModel).filter(UsuarioModel.email == "admin@flymetrics.co").first()
    if admin:
        admin.contraseña = hash_password("admin123456")
    else:
        admin = UsuarioModel(email="admin@flymetrics.co", contraseña=hash_password("admin123456"), rol="administrador")
        db.add(admin)
    
    # Tecnico
    tech_user = db.query(UsuarioModel).filter(UsuarioModel.email == "tecnico@flymetrics.co").first()
    if tech_user:
        tech_user.contraseña = hash_password("tecnico123456")
    else:
        tech_user = UsuarioModel(email="tecnico@flymetrics.co", contraseña=hash_password("tecnico123456"), rol="tecnico")
        db.add(tech_user)
        db.commit()
        db.refresh(tech_user)
        tech_profile = TecnicoModel(id_usuario=tech_user.id_usuarios, nombre="Carlos", apellido_1="Pérez", certificacion="Piloto RPAS", estado="disponible", servicios_capacitados="Fotogrametria")
        db.add(tech_profile)

    # Cliente
    client_user = db.query(UsuarioModel).filter(UsuarioModel.email == "cliente@flymetrics.co").first()
    if client_user:
        client_user.contraseña = hash_password("cliente123456")
    else:
        client_user = UsuarioModel(email="cliente@flymetrics.co", contraseña=hash_password("cliente123456"), rol="cliente")
        db.add(client_user)
        db.commit()
        db.refresh(client_user)
        client_profile = ClienteModel(id_usuario=client_user.id_usuarios, nombre="Juan", apellido_1="Gómez", verificado=True)
        db.add(client_profile)

    db.commit()

ensure_users()

def get_token_for(email, password):
    res = client.post("/api/v1/auth/login", json={"email": email, "contraseña": password})
    assert res.status_code == 200, f"Error al autenticar {email}: {res.text}"
    body = res.json()
    if "data" in body and "token" in body["data"]:
        return body["data"]["token"]
    elif "access_token" in body:
        return body["access_token"]
    raise KeyError(f"Formato de respuesta desconocido: {body}")

# 1. TEST LOGIN ADMIN
print("\n1. Probando Login de Administrador...")
admin_token = get_token_for("admin@flymetrics.co", "admin123456")
print("   [✓] Login Admin exitoso. Token obtenido.")

headers_admin = {"Authorization": f"Bearer {admin_token}"}
r_me_admin = client.get("/api/v1/auth/me", headers=headers_admin)
assert r_me_admin.status_code == 200 and r_me_admin.json()["data"]["rol"] == "administrador"
print("   [✓] Endpoint /auth/me retornó rol 'administrador'.")

r_users_admin = client.get("/api/v1/admin/usuarios", headers=headers_admin)
assert r_users_admin.status_code == 200, f"Error obteniendo usuarios admin: {r_users_admin.text}"
print(f"   [✓] Admin puede listar todos los usuarios ({len(r_users_admin.json()['data'])} usuarios en BD).")

# 2. TEST LOGIN TÉCNICO
print("\n2. Probando Login de Técnico...")
tech_token = get_token_for("tecnico@flymetrics.co", "tecnico123456")
print("   [✓] Login Técnico exitoso. Token obtenido.")

headers_tech = {"Authorization": f"Bearer {tech_token}"}
r_me_tech = client.get("/api/v1/auth/me", headers=headers_tech)
assert r_me_tech.status_code == 200 and r_me_tech.json()["data"]["rol"] == "tecnico"
print("   [✓] Endpoint /auth/me retornó rol 'tecnico'.")

# 3. TEST LOGIN CLIENTE
print("\n3. Probando Login de Cliente...")
cli_token = get_token_for("cliente@flymetrics.co", "cliente123456")
print("   [✓] Login Cliente exitoso. Token obtenido.")

headers_cli = {"Authorization": f"Bearer {cli_token}"}
r_me_cli = client.get("/api/v1/auth/me", headers=headers_cli)
assert r_me_cli.status_code == 200 and r_me_cli.json()["data"]["rol"] == "cliente"
print("   [✓] Endpoint /auth/me retornó rol 'cliente'.")

r_fincas_cli = client.get("/api/v1/fincas", headers=headers_cli)
assert r_fincas_cli.status_code == 200
print("   [✓] Cliente puede acceder a sus fincas privadas.")

# 4. TEST ROLE SECURITY ENFORCEMENT
print("\n4. Verificando Seguridad de Roles (Un cliente NO puede acceder a endpoints de administración)...")
r_forbidden = client.get("/api/v1/admin/usuarios", headers=headers_cli)
assert r_forbidden.status_code in [403, 401], f"Falla de seguridad: Cliente pudo acceder a /admin/usuarios ({r_forbidden.status_code})"
print("   [✓] Bloqueo de seguridad verificado correctamente (HTTP 403 Forbidden al cliente en endpoints admin).")

db.close()

print("\n" + "="*80)
print("  🎉 TODAS LAS AUTENTICACIONES Y ROLES FUNCIONAN PERFECTAMENTE Y SIN NINGÚN GLITCH")
print("="*80)
