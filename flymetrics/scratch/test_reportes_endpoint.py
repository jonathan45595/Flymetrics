import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient
from main import app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel
from app.infrastructure.security.jwt_handler import create_access_token

client = TestClient(app)
db = SessionLocal()
admin_user = db.query(UsuarioModel).filter(UsuarioModel.rol == "administrador").first()
token = create_access_token({"sub": admin_user.email, "rol": "administrador", "id_usuarios": admin_user.id_usuarios})
headers = {"Authorization": f"Bearer {token}"}

res = client.get("/api/v1/reportes-vuelo", headers=headers)
print("Status /reportes-vuelo:", res.status_code)
print("Response data:", res.json())
assert res.status_code == 200, res.text
print("✓ /api/v1/reportes-vuelo FUNCIONA PERFECTAMENTE Y RESPONDE HTTP 200")
