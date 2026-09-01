import sys
import os
from datetime import date, datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from fastapi.testclient import TestClient  # type: ignore
from main import app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, FincaModel, ServicioModel, AgendaModel, EntregableModel, PagoModel, PQRModel, DroneModel, TecnicoModel
)
from app.infrastructure.security.jwt_handler import hash_password

client = TestClient(app)
db = SessionLocal()

print("==========================================================================")
print("  AUDITORÍA Y PRUEBA DE CASOS DE USO INTEGRALES (CLIENTE, CAMBIOS, DESCARGAS)")
print("==========================================================================\n")

# Setup clean test environment
def get_user_token(email, password, role="cliente"):
    u = db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
    if u:
        u.contraseña = hash_password(password)
        u.rol = role
    else:
        u = UsuarioModel(email=email, contraseña=hash_password(password), rol=role)
        db.add(u)
    db.commit()
    db.refresh(u)
    
    # Ensure profile
    if role == "cliente":
        c = db.query(ClienteModel).filter(ClienteModel.id_usuario == u.id_usuarios).first()
        if not c:
            c = ClienteModel(id_usuario=u.id_usuarios, nombre="Test", apellido_1="Client", verificado=True)
            db.add(c)
            db.commit()
    elif role == "administrador":
        pass
    
    res = client.post("/api/v1/auth/login", json={"email": email, "contraseña": password})
    assert res.status_code == 200, f"Login falló para {email}: {res.text}"
    data = res.json()["data"] if "data" in res.json() else res.json()
    return data.get("token") or data.get("access_token"), u

admin_token, admin_user = get_user_token("usecase_admin@flymetrics.co", "admin123", "administrador")
client_token, client_user = get_user_token("usecase_client@flymetrics.co", "client123", "cliente")
h_admin = {"Authorization": f"Bearer {admin_token}"}
h_client = {"Authorization": f"Bearer {client_token}"}

# 1. CASO DE USO: REGISTRO Y GESTIÓN DE FINCAS POR EL CLIENTE
print("--- 1. Probando Caso de Uso: Registro y Modificación de Fincas por Cliente ---")
finca_req = {
    "id_cliente": 1,
    "nombre_finca": "Hacienda El Dron Casanare",
    "ubicacion_municipio": "Yopal",
    "departamento": "Casanare",
    "hectareas": 45.5,
    "latitud": 5.348,
    "longitud": -72.395
}
r_finca = client.post("/api/v1/fincas", json=finca_req, headers=h_client)
print(f"  [+] Registro Finca: HTTP {r_finca.status_code}")
assert r_finca.status_code == 201, f"Error creando finca: {r_finca.text}"
id_finca = r_finca.json()["data"]["id_finca"]

# Modificar Finca
r_finca_upd = client.put(f"/api/v1/fincas/{id_finca}", json={"nombre_finca": "Hacienda El Dron Casanare Actualizada", "hectareas": 50.0}, headers=h_client)
print(f"  [+] Modificación Finca: HTTP {r_finca_upd.status_code}")
assert r_finca_upd.status_code == 200

# 2. CASO DE USO: SOLICITUD DE SERVICIO / COTIZACIÓN Y FECHA DE MUESTREO
print("\n--- 2. Probando Caso de Uso: Cotización y Agendamiento (Fecha de Muestreo) ---")
# Obtener servicio
serv = db.query(ServicioModel).first()
if not serv:
    serv = ServicioModel(nombre_servicio="Fotogrametría NDVI", descripcion="Muestreo multiespectral", precio_base_m2=150.0)
    db.add(serv)
    db.commit()
    db.refresh(serv)

# Cotización
r_coti = client.post("/api/v1/servicios/cotizar", json={"id_servicio": serv.id_servicio, "id_finca": id_finca}, headers=h_client)
print(f"  [+] Cotización de Servicio: HTTP {r_coti.status_code}")
assert r_coti.status_code in [200, 201]

# Agendar Turno / Muestreo
fecha_muestreo = (date.today() + timedelta(days=2)).isoformat()
agenda_req = {
    "id_finca": id_finca,
    "id_servicio": serv.id_servicio,
    "fecha_de_turno": fecha_muestreo,
    "tipo_turno": "Fumigación",
    "observaciones_servicio": "Muestreo urgente de lote 3"
}
r_ag = client.post("/api/v1/agenda/reservar", json=agenda_req, headers=h_client)
print(f"  [+] Reserva Turno Muestreo: HTTP {r_ag.status_code}")
assert r_ag.status_code in [200, 201], f"Error al agendar: {r_ag.text}"
id_turno = r_ag.json()["data"]["id_turno"]

# 3. CASO DE USO: CAMBIOS DE FECHA DE MUESTREO Y ESTADO
print("\n--- 3. Probando Caso de Uso: Cambios en Fecha de Muestreo (Reprogramación) ---")
nueva_fecha = (date.today() + timedelta(days=5)).isoformat()
r_change_date = client.put(f"/api/v1/agenda/{id_turno}", json={"fecha_de_turno": nueva_fecha, "estado": "Confirmado"}, headers=h_admin)
print(f"  [+] Reprogramación Fecha Muestreo (Admin): HTTP {r_change_date.status_code}")
assert r_change_date.status_code == 200

# 4. CASO DE USO: SUBIDA Y DESCARGA DE ENTREGABLES (MAPAS / INFORME PDF)
print("\n--- 4. Probando Caso de Uso: Entrega y Descarga de Mapas / Reporte PDF ---")
entregable_req = {
    "id_turno": id_turno,
    "tipo_archivo": "Ortofoto NDVI",
    "url_archivo": "/uploads/entregables/ortofoto_test.pdf",
    "nombre_archivo": "Reporte_Multiespectral_Lote3.pdf"
}
r_ent = client.post("/api/v1/entregables", json=entregable_req, headers=h_admin)
print(f"  [+] Subida/Registro de Entregable: HTTP {r_ent.status_code}")
assert r_ent.status_code == 201
id_entregable = r_ent.json()["data"]["id_entregable"]

# Consulta del buzón cliente
r_buzon = client.get("/api/v1/entregables/mis-archivos", headers=h_client)
print(f"  [+] Consulta Buzón de Entregables por Cliente: HTTP {r_buzon.status_code} ({len(r_buzon.json()['data'])} archivos)")
assert r_buzon.status_code == 200

# Descarga Directa de Entregable / PDF
r_dl = client.get(f"/api/v1/entregables/{id_entregable}/descargar")
print(f"  [+] Descarga Directa de Entregable PDF: HTTP {r_dl.status_code} (Content-Type: {r_dl.headers.get('content-type')})")
assert r_dl.status_code == 200 and r_dl.headers.get("content-type") == "application/pdf"

# 5. CASO DE USO: CAMBIO DE ROL DE USUARIO POR ADMINISTRADOR
print("\n--- 5. Probando Caso de Uso: Cambio de Rol de Usuario por Admin ---")
# Crear un nuevo usuario temporal
r_newuser = client.post("/api/v1/admin/usuarios", json={
    "email": "user_role_change@flymetrics.co",
    "contraseña": "password123",
    "rol": "cliente",
    "nombre": "Pedro",
    "apellido_1": "Ramírez"
}, headers=h_admin)
print(f"  [+] Creación de Usuario: HTTP {r_newuser.status_code}")
assert r_newuser.status_code == 201
id_user_change = r_newuser.json()["data"]["id_usuarios"]

# Cambiar su rol a técnico
r_role = client.put(f"/api/v1/admin/usuarios/{id_user_change}/rol", json={"rol": "tecnico"}, headers=h_admin)
print(f"  [+] Cambio de Rol a 'tecnico': HTTP {r_role.status_code}")
assert r_role.status_code == 200 and r_role.json()["data"]["rol"] == "tecnico"

# 6. CASO DE USO: GESTIÓN DE PQRS Y SOPORTE AL CLIENTE
print("\n--- 6. Probando Caso de Uso: Registro y Respuesta a PQR por Cliente ---")
pqr_req = {
    "tipo": "peticion",
    "asunto": "Consulta sobre resolución de mapa NDVI",
    "mensaje": "Solicito información sobre los canales espectrales del dron."
}
r_pqr = client.post("/api/v1/pqrs", json=pqr_req, headers=h_client)
print(f"  [+] Registro de PQR por Cliente: HTTP {r_pqr.status_code}")
assert r_pqr.status_code == 201

db.close()

print("\n" + "="*80)
print("  🎉 TODOS LOS CASOS DE USO (CLIENTE, CAMBIOS DE FECHA, CAMBIOS DE ROL, DESCARGAS) FUNCIONAN 100% PERFECTO")
print("="*80)
