import sys
sys.path.insert(0, '.')
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, TecnicoModel, DroneModel,
    ServicioModel, FincaModel, AgendaModel, PagoModel
)

db = SessionLocal()
print("USUARIOS:")
for u in db.query(UsuarioModel).all():
    print(f"  id: {u.id_usuarios}, email: {u.email}, rol: {u.rol}")

print("\nCLIENTES:")
for c in db.query(ClienteModel).all():
    print(f"  id: {c.id_cliente}, nombre: {c.nombre} {c.apellido_1}, user_id: {c.id_usuario}")

print("\nTECNICOS:")
for t in db.query(TecnicoModel).all():
    print(f"  id: {t.id_tecnico}, nombre: {t.nombre} {t.apellido_1}, user_id: {t.id_usuario}, estado: {t.estado}")

print("\nDRONES:")
for d in db.query(DroneModel).all():
    print(f"  id: {d.id_drone}, modelo: {d.modelo}, serie: {d.numero_serie}, estado: {d.estado}")

print("\nFINCAS:")
for f in db.query(FincaModel).all():
    print(f"  id: {f.id_finca}, nombre: {f.nombre_finca}, cliente_id: {f.id_cliente}")

print("\nAGENDA:")
for a in db.query(AgendaModel).all():
    print(f"  id: {a.id_turno}, finca_id: {a.id_finca}, servicio_id: {a.id_servicio}, tecnico_id: {a.id_tecnico}, drone_id: {a.id_drone}, estado: {a.estado}")

db.close()
