r"""
Script to ensure admin and tecnico users exist in the database.
Run with: .venv\Scripts\python scratch\ensure_staff.py
"""
import sys, os
sys.path.insert(0, '.')

from sqlalchemy.orm import Session
from app.infrastructure.database.session import SessionLocal
from app.application.use_cases.use_cases import AuthUseCases
from app.application.dto.schemas import UsuarioCreate
from app.infrastructure.database.models.models import UsuarioModel

db: Session = SessionLocal()

STAFF = [
    {
        "email": "admin@flymetrics.co",
        "contraseña": "admin123",
        "rol": "administrador",
        "nombre": "Admin",
        "apellido_1": "Principal",
    },
    {
        "email": "tecnico@flymetrics.co",
        "contraseña": "tecnico123",
        "rol": "tecnico",
        "nombre": "Carlos",
        "apellido_1": "Técnico",
        "telefono": "3001234567",
        "certificacion": "Piloto RPAS Nivel A"
    },
    {
        "email": "tecnico2@flymetrics.co",
        "contraseña": "tecnico123",
        "rol": "tecnico",
        "nombre": "Ana",
        "apellido_1": "Gómez",
        "telefono": "3209998888",
        "certificacion": "Piloto RPAS Nivel B"
    },
]

print("[STAFF SEED] Starting...")
for u in STAFF:
    exists = db.query(UsuarioModel).filter(UsuarioModel.email == u["email"]).first()
    if exists:
        print(f"  [i] Already exists: {u['email']} (rol: {exists.rol})")
        continue
    try:
        req = UsuarioCreate(**u)
        user = AuthUseCases.register_user(db, req)
        print(f"  [+] Created: {u['email']} / {u['contraseña']}  (rol: {user.rol})")
    except Exception as e:
        print(f"  [!] Error creating {u['email']}: {e}")

db.close()
print("[STAFF SEED] DONE!")
print()
print("=" * 50)
print("CREDENTIALS FOR TESTING:")
print("  Admin:   admin@flymetrics.co / admin123")
print("  Técnico: tecnico@flymetrics.co / tecnico123")
print("  Técnico: tecnico2@flymetrics.co / tecnico123")
print("  Cliente: cliente.demo@flymetrics.co / cliente123")
print("=" * 50)
