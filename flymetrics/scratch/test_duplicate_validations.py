import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.getcwd())
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=== PROBANDO VALIDACIONES DE BASE DE DATOS (CORREO, TELÉFONO, PASSWORD) ===")

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel
from app.infrastructure.security.jwt_handler import create_access_token

db = SessionLocal()
admin_user = db.query(UsuarioModel).filter(UsuarioModel.rol == "administrador").first()
token = create_access_token({"sub": admin_user.email, "rol": "administrador", "id_usuarios": admin_user.id_usuarios})
headers = {"Authorization": f"Bearer {token}"}

# 2. Duplicate email registration
res_dup_email = client.post("/api/v1/auth/register", json={
    "email": "admin@flymetrics.co",
    "contraseña": "password123",
    "rol": "cliente",
    "nombre": "Test",
    "apellido_1": "Dup",
    "telefono": "3999999999"
})
print("Duplicate email status:", res_dup_email.status_code, "->", res_dup_email.json())
assert res_dup_email.status_code == 400
assert "ya se encuentra registrado" in res_dup_email.json().get("message", "")

# 3. Duplicate phone registration
# First create a test user
res_u1 = client.post("/api/v1/auth/register", json={
    "email": "unique_user_test_99@gmail.com",
    "contraseña": "password123",
    "rol": "cliente",
    "nombre": "User",
    "apellido_1": "Unique",
    "telefono": "3118889977"
})
print("Create test user 1:", res_u1.status_code)

# Try with same phone
res_dup_phone = client.post("/api/v1/auth/register", json={
    "email": "another_unique_user_88@gmail.com",
    "contraseña": "password123",
    "rol": "cliente",
    "nombre": "User2",
    "apellido_1": "Unique2",
    "telefono": "3118889977"
})
print("Duplicate phone status:", res_dup_phone.status_code, "->", res_dup_phone.json())
assert res_dup_phone.status_code == 400
assert "número telefónico" in res_dup_phone.json().get("message", "")

# 4. Change password test
res_change_pwd = client.put(f"/api/v1/admin/usuarios/{admin_user.id_usuarios}", json={"contraseña": "newPassword123!"}, headers=headers)
print("Admin update password status:", res_change_pwd.status_code)
assert res_change_pwd.status_code == 200

# Revert admin password
client.put(f"/api/v1/admin/usuarios/{admin_user.id_usuarios}", json={"contraseña": "password123"}, headers=headers)

# Clean up test user
u_test = db.query(UsuarioModel).filter(UsuarioModel.email == "unique_user_test_99@gmail.com").first()
if u_test:
    db.delete(u_test)
    db.commit()

print("\n✓ TODAS LAS VALIDACIONES DE DUPLICADOS Y CONTRASEÑAS FUNCIONAN AL 100%")
