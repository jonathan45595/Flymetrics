import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel
from app.presentation.api.routers.bitacora import get_tecnico_agenda

db = SessionLocal()
try:
    user = db.query(UsuarioModel).filter(UsuarioModel.rol == "tecnico").first()
    res = get_tecnico_agenda(fecha=None, estado=None, db=db, current_user=user)
    print("BODY:", res.body.decode('utf-8'))
except Exception as e:
    print("CRASH:", e)
finally:
    db.close()
