import sys
sys.path.insert(0, '.')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel
from app.infrastructure.security.jwt_handler import hash_password, create_access_token
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
db = SessionLocal()

print("=== INICIANDO PRUEBA DE TRANSFERENCIA DE NIT ENTRE CUENTAS ===")

# Limpiar usuarios de prueba si existen
email_ant = "cuenta_antigua_nit@test.com"
email_nue = "cuenta_nueva_nit@test.com"
nit_prueba = "901999888-1"

u_ant = db.query(UsuarioModel).filter(UsuarioModel.email == email_ant).first()
if u_ant:
    db.query(ClienteModel).filter(ClienteModel.id_usuario == u_ant.id_usuarios).delete()
    db.delete(u_ant)

u_nue = db.query(UsuarioModel).filter(UsuarioModel.email == email_nue).first()
if u_nue:
    db.query(ClienteModel).filter(ClienteModel.id_usuario == u_nue.id_usuarios).delete()
    db.delete(u_nue)

db.commit()

# 1. Crear Cuenta Anterior (Titular original del NIT)
u_ant = UsuarioModel(
    email=email_ant,
    contraseña=hash_password("claveAnterior123"),
    rol="cliente"
)
db.add(u_ant)
db.flush()

c_ant = ClienteModel(
    id_usuario=u_ant.id_usuarios,
    nombre="AgroInversiones",
    apellido_1="del Valle",
    numero_documento=nit_prueba,
    fecha_nacimiento="1980-01-01",
    verificado=True
)
db.add(c_ant)
db.commit()
print(f"1. Cuenta anterior creada con NIT {nit_prueba} y verificado=True (Titular: AgroInversiones del Valle)")

# 2. Crear Cuenta Nueva (Intenta verificar el mismo NIT)
u_nue = UsuarioModel(
    email=email_nue,
    contraseña=hash_password("claveNueva456"),
    rol="cliente"
)
db.add(u_nue)
db.flush()

c_nue = ClienteModel(
    id_usuario=u_nue.id_usuarios,
    nombre="NuevoPropietario",
    apellido_1="SAS",
    numero_documento=None,
    fecha_nacimiento="1995-05-15",
    verificado=False
)
db.add(c_nue)
db.commit()
print(f"2. Cuenta nueva creada sin NIT y verificado=False")

token_nue = create_access_token({"sub": email_nue, "rol": "cliente", "id_usuarios": u_nue.id_usuarios})
headers_nue = {"Authorization": f"Bearer {token_nue}"}

# 3. Intentar verificar la cuenta nueva con el NIT de la cuenta anterior -> Debe responder 409 Conflict con nombre del titular
r1 = client.post("/api/v1/clientes/completar-verificacion", headers=headers_nue, json={
    "numero_documento": nit_prueba,
    "nombre": "NuevoPropietario",
    "apellido_1": "SAS",
    "fecha_nacimiento": "1995-05-15"
})

print(f"3. Intento de verificación sin contraseña -> Status: {r1.status_code}")
assert r1.status_code == 409, f"Esperaba 409, obtuve {r1.status_code}: {r1.text}"
body1 = r1.json()
print("   Mensaje de error:", body1.get("message"))
err_detail = body1.get("errors", [{}])[0]
print("   Nombre titular devuelto:", err_detail.get("nombre_titular"))
print("   Email titular devuelto:", err_detail.get("email_titular"))
assert "AgroInversiones del Valle" in err_detail.get("nombre_titular", "")
assert email_ant == err_detail.get("email_titular", "")

# 4. Intentar con contraseña incorrecta de la cuenta anterior -> Debe responder 401
r2 = client.post("/api/v1/clientes/completar-verificacion", headers=headers_nue, json={
    "numero_documento": nit_prueba,
    "nombre": "NuevoPropietario",
    "apellido_1": "SAS",
    "fecha_nacimiento": "1995-05-15",
    "transfer_password": "claveIncorrecta"
})
print(f"4. Intento con contraseña incorrecta -> Status: {r2.status_code}")
assert r2.status_code == 401, f"Esperaba 401, obtuve {r2.status_code}"

# 5. Autorizar transferencia con contraseña correcta de la cuenta anterior -> Debe responder 200 OK
r3 = client.post("/api/v1/clientes/completar-verificacion", headers=headers_nue, json={
    "numero_documento": nit_prueba,
    "nombre": "NuevoPropietario",
    "apellido_1": "SAS",
    "fecha_nacimiento": "1995-05-15",
    "transfer_password": "claveAnterior123"
})
print(f"5. Transferencia autorizada con contraseña correcta -> Status: {r3.status_code}")
assert r3.status_code == 200, f"Esperaba 200, obtuve {r3.status_code}: {r3.text}"

# 6. Comprobar estados en base de datos
id_u_nue = u_nue.id_usuarios
id_u_ant = u_ant.id_usuarios
db.close()
db = SessionLocal()

c_nue_db = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_u_nue).first()
c_ant_db = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_u_ant).first()

print(f"6. Verificación en BD:")
print(f"   Cuenta Nueva: NIT={c_nue_db.numero_documento}, Verificado={c_nue_db.verificado}")
print(f"   Cuenta Anterior: NIT={c_ant_db.numero_documento}, Verificado={c_ant_db.verificado}")

assert c_nue_db.numero_documento == nit_prueba
assert c_nue_db.verificado == True
assert c_ant_db.numero_documento is None
assert c_ant_db.verificado == False


print("\n>>> ¡TODAS LAS PRUEBAS DE CONFLICTO Y TRANSFERENCIA DE NIT PASARON EXITOSAMENTE! <<<")
