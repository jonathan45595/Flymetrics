import sys
import os
# Add root path to Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, TecnicoModel
from app.infrastructure.security.jwt_handler import hash_password

def seed():
    db = SessionLocal()
    try:
        # 1. Seed Admin
        admin_email = "admin@flymetrics.co"
        admin_user = db.query(UsuarioModel).filter(UsuarioModel.email == admin_email).first()
        if not admin_user:
            admin_user = UsuarioModel(
                email=admin_email,
                contraseña=hash_password("admin123"), # Wait, python model uses contraseña or contrasenia? Let's check model definition.
                # Actually, the model uses contraseña (let's verify, yes, contraseña is used in create_admin_cli.py)
                rol="administrador"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"[+] Admin created: {admin_email}")
        else:
            print(f"[~] Admin already exists: {admin_email}")

        # 2. Seed Technician User
        tech_email = "tecnico@flymetrics.co"
        tech_user = db.query(UsuarioModel).filter(UsuarioModel.email == tech_email).first()
        if not tech_user:
            tech_user = UsuarioModel(
                email=tech_email,
                contraseña=hash_password("tecnico123"),
                rol="tecnico"
            )
            db.add(tech_user)
            db.commit()
            db.refresh(tech_user)
            print(f"[+] Tech user created: {tech_email}")
        else:
            print(f"[~] Tech user already exists: {tech_email}")

        # 3. Seed Technician Profile
        tech_profile = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == tech_user.id_usuarios).first()
        if not tech_profile:
            tech_profile = TecnicoModel(
                id_usuario=tech_user.id_usuarios,
                nombre="Técnico",
                apellido_1="Soporte",
                apellido_2="Flymetrics",
                telefono="3001234567",
                certificacion="Certificación Civil RAC 91",
                estado="disponible"
            )
            db.add(tech_profile)
            db.commit()
            print("[+] Technician profile created successfully")
        else:
            print("[~] Technician profile already exists")

    except Exception as e:
        db.rollback()
        print(f"[-] Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
