import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from fastapi.testclient import TestClient  # type: ignore
from main import app
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, TecnicoModel, FincaModel,
    EntregableModel, PagoModel, PQRModel
)
from app.infrastructure.security.jwt_handler import hash_password

client = TestClient(app)
db = SessionLocal()

OK  = "  [OK]"
ERR = "  [FALLO]"
SEP = "-" * 76
passed = 0
failed = 0
errors = []

def check(desc, cond, extra=""):
    global passed, failed
    if cond:
        print(f"{OK} {desc}")
        passed += 1
    else:
        print(f"{ERR} {desc}" + (f" | {extra}" if extra else ""))
        failed += 1
        errors.append(desc)

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

# ─── SEED USUARIOS ────────────────────────────────────────────────────────────
def ensure_users():
    admin = db.query(UsuarioModel).filter(UsuarioModel.email == "admin@flymetrics.co").first()
    if admin:
        admin.contraseña = hash_password("Admin#1234")
    else:
        admin = UsuarioModel(email="admin@flymetrics.co", contraseña=hash_password("Admin#1234"), rol="administrador")
        db.add(admin)

    tec = db.query(UsuarioModel).filter(UsuarioModel.email == "tecnico.test@flymetrics.co").first()
    if not tec:
        tec = UsuarioModel(email="tecnico.test@flymetrics.co", contraseña=hash_password("Tecnico#1234"), rol="tecnico")
        db.add(tec)
        db.flush()
        db.add(TecnicoModel(id_usuario=tec.id_usuarios, nombre="Carlos", apellido_1="Tecnico", estado="Activo"))
    else:
        tec.contraseña = hash_password("Tecnico#1234")

    cli = db.query(UsuarioModel).filter(UsuarioModel.email == "cliente.test@flymetrics.co").first()
    if not cli:
        cli = UsuarioModel(email="cliente.test@flymetrics.co", contraseña=hash_password("Cliente#1234"), rol="cliente")
        db.add(cli)
        db.flush()
        db.add(ClienteModel(id_usuario=cli.id_usuarios, nombre="Maria", apellido_1="Cliente", verificado=True))
    else:
        cli.contraseña = hash_password("Cliente#1234")

    db.commit()

ensure_users()

def login_as(email, pwd):
    r = client.post("/api/v1/auth/login", json={"email": email, "contrasena": pwd})
    if r.status_code != 200:
        r = client.post("/api/v1/auth/login", json={"email": email, "contraseña": pwd})
    if r.status_code == 200:
        return r.json().get("data", {}).get("token")
    return None

section("0. TOKENS DE ACCESO")
admin_token   = login_as("admin@flymetrics.co", "Admin#1234")
tecnico_token = login_as("tecnico.test@flymetrics.co", "Tecnico#1234")
cliente_token = login_as("cliente.test@flymetrics.co", "Cliente#1234")
check("Login Admin", bool(admin_token))
check("Login Tecnico", bool(tecnico_token))
check("Login Cliente", bool(cliente_token))

ah = {"Authorization": f"Bearer {admin_token}"}
th = {"Authorization": f"Bearer {tecnico_token}"}
ch = {"Authorization": f"Bearer {cliente_token}"}

section("1. AUTH /me PARA CADA ROL")
r = client.get("/api/v1/auth/me", headers=ah)
check("Admin /auth/me rol=administrador", r.status_code==200 and r.json().get("data",{}).get("rol")=="administrador", r.text[:80])
r = client.get("/api/v1/auth/me", headers=th)
check("Tecnico /auth/me rol=tecnico", r.status_code==200 and r.json().get("data",{}).get("rol")=="tecnico", r.text[:80])
r = client.get("/api/v1/auth/me", headers=ch)
check("Cliente /auth/me rol=cliente", r.status_code==200 and r.json().get("data",{}).get("rol")=="cliente", r.text[:80])
r = client.post("/api/v1/auth/login", json={"email":"admin@flymetrics.co","contraseña":"WRONG"})
check("Login contrasena incorrecta -> 400/401", r.status_code in (400,401,422), r.text[:80])

section("2. REGISTRO NUEVO USUARIO")
new_email = "nuevo.e2e.maestro@flymetrics.co"
ex = db.query(UsuarioModel).filter(UsuarioModel.email==new_email).first()
if ex:
    db.delete(ex); db.commit()
r = client.post("/api/v1/auth/register", json={"email":new_email,"contraseña":"Nuevo#1234","rol":"cliente"})
check("Registro nuevo usuario -> 201", r.status_code==201, r.text[:80])
new_token = login_as(new_email, "Nuevo#1234")
check("Nuevo usuario puede hacer login", bool(new_token))

section("3. HEALTH CHECK")
r = client.get("/api/v1/health")
check("GET /api/v1/health -> 200", r.status_code==200, r.text[:60])

section("4. ADMIN - USUARIOS")
r = client.get("/api/v1/admin/usuarios", headers=ah)
check("Admin: listar usuarios -> 200", r.status_code==200, r.text[:80])
ucount = len(r.json().get("data",[]))
check("Al menos 3 usuarios en BD", ucount>=3, f"Encontrados: {ucount}")
r = client.get("/api/v1/admin/usuarios", headers=ch)
check("Cliente NO puede listar usuarios (403)", r.status_code==403, r.text[:60])

section("5. TECNICOS - CRUD")
r = client.get("/api/v1/tecnicos", headers=ah)
check("Admin: listar tecnicos -> 200", r.status_code==200, r.text[:80])
tecnicos = r.json().get("data",[])
check("Al menos 1 tecnico registrado", len(tecnicos)>=1, f"Encontrados: {len(tecnicos)}")
id_tec = tecnicos[0]["id_tecnico"] if tecnicos else None
if id_tec:
    r = client.get(f"/api/v1/tecnicos/{id_tec}", headers=ah)
    check(f"Admin: detalle tecnico #{id_tec} -> 200", r.status_code==200, r.text[:60])
    r = client.put(f"/api/v1/tecnicos/{id_tec}", headers=ah, json={"estado":"Activo"})
    check(f"Admin: actualizar tecnico #{id_tec} -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/tecnicos", headers=th)
check("Tecnico: puede listar tecnicos -> 200", r.status_code==200, r.text[:60])

section("6. CLIENTES - CRUD")
r = client.get("/api/v1/clientes", headers=ah)
check("Admin: listar clientes -> 200", r.status_code==200, r.text[:80])
clientes = r.json().get("data",[])
check("Al menos 1 cliente registrado", len(clientes)>=1, f"Encontrados: {len(clientes)}")
id_cli = clientes[0]["id_cliente"] if clientes else None
if id_cli:
    r = client.get(f"/api/v1/clientes/{id_cli}", headers=ah)
    check(f"Admin: detalle cliente #{id_cli} -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/clientes/me", headers=ch)
check("Cliente: /clientes/me -> 200", r.status_code==200, r.text[:60])
mi_cli = r.json().get("data",{})
if mi_cli.get("id_cliente"):
    r = client.put(f"/api/v1/clientes/{mi_cli['id_cliente']}", headers=ch, json={"nombre":"MariaUpdated","apellido_1":"Cliente"})
    check("Cliente: actualizar propio perfil -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/clientes", headers=ch)
check("Cliente NO puede listar clientes (403)", r.status_code==403, r.text[:60])

section("7. FINCAS - CRUD")
# Obtener id_cliente del perfil autenticado
id_cli_para_finca = mi_cli.get("id_cliente") or (id_cli or 1)
r = client.post("/api/v1/fincas", headers=ch, json={
    "id_cliente": id_cli_para_finca,
    "nombre_finca":"Finca E2E Test","ubicacion_municipio":"Palmira",
    "departamento":"Valle del Cauca","hectareas":20.0,
    "latitud":3.5394,"longitud":-76.3031
})
check("Cliente: crear finca -> 201", r.status_code==201, r.text[:80])
id_finca_new = r.json().get("data",{}).get("id_finca") if r.status_code==201 else None
r = client.get("/api/v1/fincas", headers=ch)
check("Cliente: listar fincas -> 200", r.status_code==200, r.text[:60])
fincas = r.json().get("data",[])
check("Al menos 1 finca", len(fincas)>=1, f"Encontradas: {len(fincas)}")
id_finca = id_finca_new or (fincas[0]["id_finca"] if fincas else None)
if id_finca:
    r = client.get(f"/api/v1/fincas/{id_finca}", headers=ch)
    check(f"Cliente: detalle finca #{id_finca} -> 200", r.status_code==200, r.text[:60])
    r = client.put(f"/api/v1/fincas/{id_finca}", headers=ch, json={"nombre_finca":"Finca E2E Actualizada","hectareas":25.0})
    check(f"Cliente: actualizar finca #{id_finca} -> 200", r.status_code==200, r.text[:60])

section("8. SERVICIOS")
r = client.get("/api/v1/servicios", headers=ch)
check("Cliente: listar servicios -> 200", r.status_code==200, r.text[:60])
servicios = r.json().get("data",[])
id_svc = servicios[0]["id_servicio"] if servicios else 1

section("9. AGENDAMIENTO - FLUJO COMPLETO")
import datetime as dt_mod
fecha_futura = (dt_mod.date.today() + dt_mod.timedelta(days=30)).isoformat()
payload = {"id_finca":id_finca or 1,"id_servicio":id_svc,"fecha_de_turno":fecha_futura,"observaciones_servicio":"Prueba E2E Maestro"}
r = client.post("/api/v1/agenda", headers=ch, json=payload)
check("Cliente: crear reserva -> 201", r.status_code==201, r.text[:100])
id_turno = r.json().get("data",{}).get("id_turno") if r.status_code==201 else None
r2 = client.post("/api/v1/agenda/reservar", headers=ch, json={**payload,"observaciones_servicio":"via /reservar"})
check("Cliente: crear reserva via /reservar -> 201", r2.status_code==201, r2.text[:80])
id_turno_alias = r2.json().get("data",{}).get("id_turno") if r2.status_code==201 else None
r = client.get("/api/v1/agenda/mis-turnos", headers=ch)
check("Cliente: listar mis-turnos -> 200", r.status_code==200, r.text[:60])
turnos = r.json().get("data",[])
check("Al menos 1 turno en agenda", len(turnos)>=1, f"Turnos: {len(turnos)}")
r = client.get("/api/v1/agenda/mis-turnos?estado=Pendiente", headers=ch)
check("Cliente: filtrar turnos estado=Pendiente -> 200", r.status_code==200, r.text[:60])
if id_turno:
    fecha_reprog = (dt_mod.date.today() + dt_mod.timedelta(days=45)).isoformat()
    r = client.put(f"/api/v1/agenda/{id_turno}", headers=ch, json={"fecha_de_turno":fecha_reprog,"observaciones_servicio":"Reprogramado E2E"})
    check(f"Cliente: reprogramar turno #{id_turno} -> 200", r.status_code==200, r.text[:60])
    r = client.patch(f"/api/v1/agenda/{id_turno}", headers=ah, json={"estado":"Confirmado"})
    check(f"Admin: PATCH estado turno #{id_turno} Confirmado -> 200", r.status_code==200, r.text[:60])
    r = client.get(f"/api/v1/agenda/estado/{id_turno}")
    check(f"Publico: estado turno #{id_turno} sin auth -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/agenda", headers=ah)
check("Admin: listar todos turnos -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/agenda?estado=Confirmado", headers=ah)
check("Admin: filtrar turnos por estado -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/admin/agenda", headers=ah)
check("Admin: /admin/agenda -> 200", r.status_code==200, r.text[:60])
if id_turno:
    r = client.patch(f"/api/v1/admin/agenda/{id_turno}/estado", headers=ah, json={"estado":"Hecho","observaciones_servicio":"Finalizado E2E"})
    check(f"Admin: forzar estado Hecho turno #{id_turno} -> 200", r.status_code==200, r.text[:60])
if id_turno_alias:
    r = client.delete(f"/api/v1/agenda/{id_turno_alias}", headers=ch)
    check(f"Cliente: cancelar turno alias #{id_turno_alias} -> 200", r.status_code==200, r.text[:60])

section("10. ENTREGABLES - SUBIR, LISTAR, DESCARGAR")
entregable_id = None
if id_turno:
    r = client.post("/api/v1/entregables", headers=ah, json={
        "id_turno":id_turno,"tipo_archivo":"NDVI",
        "url_archivo":"https://storage.flymetrics.co/mapas/ndvi_e2e.tif",
        "nombre_archivo":"ndvi_e2e.tif","notas":"Mapa E2E"
    })
    check("Admin: subir entregable JSON -> 201", r.status_code==201, r.text[:80])
    entregable_id = r.json().get("data",{}).get("id_entregable") if r.status_code==201 else None
r = client.get("/api/v1/entregables", headers=th)
check("Tecnico: listar entregables -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/entregables/mis-archivos", headers=ch)
check("Cliente: buzon mis-archivos -> 200", r.status_code==200, r.text[:60])
if entregable_id:
    r = client.get(f"/api/v1/entregables/{entregable_id}/descargar")
    check(f"Publico: descargar entregable #{entregable_id} -> 200", r.status_code==200, r.text[:60])
    check("Descarga: content-type PDF", "pdf" in r.headers.get("content-type","").lower(), r.headers.get("content-type"))
r = client.post("/api/v1/entregables", headers=ch, json={"id_turno":id_turno or 1,"tipo_archivo":"Ortofoto","url_archivo":"http://hack.com/bad.tif","nombre_archivo":"hack.tif"})
check("Cliente NO puede subir entregables (403)", r.status_code==403, r.text[:60])

section("11. PAGOS - REGISTRAR, LISTAR, ACTUALIZAR")
pago_id = None
if id_turno:
    r = client.post("/api/v1/pagos", headers=ah, json={"id_turno":id_turno,"monto":750000.0,"metodo_pago":"Transferencia","estado_pago":"Pendiente"})
    check("Admin: registrar pago -> 201", r.status_code==201, r.text[:80])
    pago_id = r.json().get("data",{}).get("id_pago") if r.status_code==201 else None
r = client.get("/api/v1/admin/pagos", headers=ah)
check("Admin: /admin/pagos -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/pagos", headers=ah)
check("Admin: /pagos alias -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/pagos/mis-pagos", headers=ch)
check("Cliente: /pagos/mis-pagos -> 200", r.status_code==200, r.text[:60])
if pago_id:
    r = client.patch(f"/api/v1/pagos/{pago_id}", headers=ah, json={"estado":"Pagado","metodo":"Transferencia"})
    check(f"Admin: actualizar pago #{pago_id} Pagado -> 200", r.status_code==200, r.text[:60])
    r = client.post(f"/api/v1/pagos/{pago_id}/subir-comprobante", headers=ch, json={"url_comprobante":"https://storage.flymetrics.co/comprobantes/test.pdf","referencia_transaccion":"TXN-E2E"})
    check(f"Cliente: subir comprobante pago #{pago_id} -> 200", r.status_code==200, r.text[:60])
r = client.post("/api/v1/pagos", headers=ch, json={"id_turno":id_turno or 1,"monto":1.0,"metodo_pago":"Efectivo"})
check("Cliente NO puede registrar pagos (403)", r.status_code==403, r.text[:60])
r = client.get("/api/v1/pagos", headers=ch)
check("Cliente NO puede listar todos pagos (403)", r.status_code==403, r.text[:60])

section("12. PQRs - ABRIR, RESPONDER, CERRAR")
pqr_id = None
r = client.post("/api/v1/pqrs", headers=ch, json={"tipo":"Queja","asunto":"PQR E2E Maestro","descripcion":"Ticket de prueba E2E completa"})
check("Cliente: abrir PQR -> 201", r.status_code==201, r.text[:80])
pqr_id = r.json().get("data",{}).get("id_pqr") if r.status_code==201 else None
r = client.get("/api/v1/pqrs", headers=ch)
check("Cliente: listar mis PQRs -> 200", r.status_code==200, r.text[:60])
r = client.get("/api/v1/pqrs", headers=ah)
check("Admin: listar todos PQRs -> 200", r.status_code==200, r.text[:60])
if pqr_id:
    r = client.get(f"/api/v1/pqrs/{pqr_id}", headers=ch)
    check(f"Cliente: detalle PQR #{pqr_id} -> 200", r.status_code==200, r.text[:60])
    r = client.post(f"/api/v1/pqrs/{pqr_id}/mensajes", headers=ah, json={"mensaje":"Estamos revisando su caso. Admin FlyMetrics"})
    check(f"Admin: responder PQR #{pqr_id} -> 201", r.status_code==201, r.text[:60])
    r = client.post(f"/api/v1/pqrs/{pqr_id}/mensajes", headers=ch, json={"mensaje":"Gracias por su respuesta."})
    check(f"Cliente: responder PQR #{pqr_id} -> 201", r.status_code==201, r.text[:60])
    r = client.post(f"/api/v1/pqrs/{pqr_id}/cerrar", headers=ah)
    check(f"Admin: cerrar PQR #{pqr_id} -> 200", r.status_code==200, r.text[:60])

section("13. DISPONIBILIDAD Y CALENDARIO DE TECNICO")
if id_tec:
    r = client.get(f"/api/v1/tecnicos/{id_tec}/disponibilidad", headers=ch, params={"fecha":"2025-06-01","id_finca":id_finca or 1,"id_servicio":id_svc})
    check(f"Cliente: disponibilidad tecnico #{id_tec} -> 200", r.status_code==200, r.text[:60])
    r = client.get(f"/api/v1/tecnicos/{id_tec}/calendario-ocupacion", headers=ah, params={"anio":2025,"mes":6})
    check(f"Admin: calendario tecnico #{id_tec} -> 200", r.status_code==200, r.text[:60])

section("14. ADMIN - ASIGNAR TECNICO Y DRON A TURNO")
if id_turno and id_tec:
    r = client.patch(f"/api/v1/admin/agenda/{id_turno}/asignar", headers=ah, json={"id_tecnico":id_tec,"id_drone":None})
    check(f"Admin: asignar tecnico al turno #{id_turno} -> 200", r.status_code==200, r.text[:60])

section("15. VERIFICACION DE CLIENTE")
if mi_cli.get("id_cliente"):
    r = client.put(f"/api/v1/clientes/{mi_cli['id_cliente']}/admin-verificar", headers=ah)
    check(f"Admin: verificar cliente #{mi_cli['id_cliente']} -> 200", r.status_code==200, r.text[:60])
r = client.post("/api/v1/clientes/completar-verificacion", headers=ch, json={"nombre":"Maria","apellido_1":"TestE2E","numero_documento":"9988776655","fecha_nacimiento":"1985-03-10"})
check("Cliente: completar verificacion datos -> 200", r.status_code==200, r.text[:60])

section("16. SEGURIDAD - BLOQUEOS ENTRE ROLES")
r = client.get("/api/v1/admin/usuarios", headers=ch)
check("Cliente NO puede listar usuarios (403)", r.status_code==403, r.text[:60])
r = client.get("/api/v1/admin/pagos", headers=ch)
check("Cliente NO puede ver admin/pagos (403)", r.status_code==403, r.text[:60])
r = client.get("/api/v1/admin/agenda", headers=ch)
check("Cliente NO puede ver admin/agenda (403)", r.status_code==403, r.text[:60])
r = client.post("/api/v1/pagos", headers=th, json={"id_turno":id_turno or 1,"monto":1.0,"metodo_pago":"Efectivo"})
check("Tecnico autorizado para registrar pagos (No 403)", r.status_code != 403, r.text[:60])
r = client.get("/api/v1/agenda/mis-turnos")
check("Sin token: /agenda/mis-turnos -> 401/403", r.status_code in (401,403), r.text[:60])
r = client.get("/api/v1/admin/usuarios")
check("Sin token: /admin/usuarios -> 401/403", r.status_code in (401,403), r.text[:60])

section("17. FRONTEND - PAGINAS HTML")
for name, path in [("index/landing","/"),("staff","/staff.html"),("cliente","/cliente.html"),("tecnico","/tecnico.html"),("admin","/admin.html")]:
    r = client.get(path)
    check(f"Frontend: '{name}' -> 200", r.status_code==200, f"HTTP {r.status_code}")

section("18. LIMPIEZA DE DATOS DE PRUEBA")
if pago_id:
    r = client.delete(f"/api/v1/pagos/{pago_id}", headers=ah)
    check(f"Admin: eliminar pago #{pago_id} -> 200", r.status_code==200, r.text[:60])
if id_finca_new:
    r = client.delete(f"/api/v1/fincas/{id_finca_new}", headers=ch)
    check(f"Cliente: eliminar finca #{id_finca_new} -> 200", r.status_code==200, r.text[:60])
u = db.query(UsuarioModel).filter(UsuarioModel.email==new_email).first()
if u:
    db.delete(u); db.commit()
    check("Limpieza: usuario nuevo eliminado", True)

# ─── RESUMEN ──────────────────────────────────────────────────────────────────
total = passed + failed
print(f"\n{'=' * 76}")
print(f"  RESULTADO FINAL: {passed}/{total} PASARON | {failed} FALLARON")
print(f"{'=' * 76}")
if failed == 0:
    print("\n  FLYMETRICS OS: FUNCIONA AL 100% - TODOS LOS FLUJOS OK\n")
else:
    print(f"\n  FALLOS ({failed}):")
    for i, e in enumerate(errors, 1):
        print(f"    {i}. {e}")
    print()
db.close()
