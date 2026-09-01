"""
Flymetrics - Full System Verification + Seed Script
Verifica TODOS los endpoints de la API y siembra datos reales si no existen.
"""
import sys, os
sys.path.insert(0, r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics")
os.chdir(r"c:\Users\MIGUEL\OneDrive\Documentos\flymetrics")

import requests
import json
from datetime import datetime, date, timedelta
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, TecnicoModel, DroneModel,
    ServicioModel, FincaModel, AgendaModel, PagoModel, ReporteVueloModel
)
from app.infrastructure.security.jwt_handler import hash_password

BASE = "http://localhost:3000/api/v1"
RESULTS = []

def log(status, msg):
    icon = "✅" if status else "❌"
    print(f"  {icon} {msg}")
    RESULTS.append((status, msg))

def get_token(email, password):
    try:
        r = requests.post(f"{BASE}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception as e:
        print(f"  ⚠ Login error: {e}")
    return None

def api(method, path, token=None, data=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if data:
        headers["Content-Type"] = "application/json"
    try:
        fn = {"GET": requests.get, "POST": requests.post, "PUT": requests.put, "PATCH": requests.patch, "DELETE": requests.delete}[method]
        r = fn(f"{BASE}{path}", json=data, headers=headers, params=params, timeout=5)
        return r.status_code, r.json() if r.content else {}
    except Exception as e:
        return 0, {"error": str(e)}

# ── SEED DATA ──────────────────────────────────────────────────────────────
def seed_all():
    db = SessionLocal()
    try:
        print("\n── SEEDING DATABASE ─────────────────────────────────────")

        # Servicios
        servicios_data = [
            {"nombre_servicio": "Fumigación aérea", "descripcion": "Aplicación de agroquímicos con sistema de aspersión de precisión.", "precio_base_m2": 0.70, "activo": True},
            {"nombre_servicio": "Fertilización", "descripcion": "Distribución aérea de fertilizantes sólidos o líquidos.", "precio_base_m2": 0.70, "activo": True},
            {"nombre_servicio": "Mapeo topográfico", "descripcion": "Generación de mapas NDVI y modelos 3D del terreno.", "precio_base_m2": 0.60, "activo": True},
            {"nombre_servicio": "Inspección de cultivos", "descripcion": "Revisión visual y análisis multiespectral de cultivos.", "precio_base_m2": 0.50, "activo": True},
        ]
        existing_srv = db.query(ServicioModel).count()
        if existing_srv == 0:
            for s in servicios_data:
                db.add(ServicioModel(**s))
            db.commit()
            print(f"  ✅ Seeded {len(servicios_data)} services")
        else:
            print(f"  ℹ {existing_srv} services already exist")

        # Drones
        drones_data = [
            {"modelo": "Sistema de Aspersión de Precisión", "numero_serie": "AGT40-001", "estado": "disponible", "horas_vuelo": 420, "tipo": "Fumigación", "ultima_revision": date(2026,5,15)},
            {"modelo": "Sistema Multiespectral Beta", "numero_serie": "M3E-002", "estado": "disponible", "horas_vuelo": 180, "tipo": "Mapeo/Inspección", "ultima_revision": date(2026,5,20)},
            {"modelo": "Sistema de Fertilización", "numero_serie": "AGT10-003", "estado": "mantenimiento", "horas_vuelo": 650, "tipo": "Fertilización", "ultima_revision": date(2026,4,10)},
        ]
        existing_drones = db.query(DroneModel).count()
        if existing_drones == 0:
            for d in drones_data:
                db.add(DroneModel(**d))
            db.commit()
            print(f"  ✅ Seeded {len(drones_data)} drones")
        else:
            print(f"  ℹ {existing_drones} drones already exist")

        # Seed a test client user + profile + finca for demo
        test_client_email = "cliente.demo@flymetrics.co"
        test_user = db.query(UsuarioModel).filter(UsuarioModel.email == test_client_email).first()
        if not test_user:
            test_user = UsuarioModel(email=test_client_email, contraseña=hash_password("cliente123"), rol="cliente")
            db.add(test_user)
            db.flush()
            cliente = ClienteModel(
                id_usuario=test_user.id_usuarios,
                nombre="Carlos", apellido_1="Mendoza", apellido_2="Ortiz",
                telefono="3001234567", verificado=1, ciudad_expedicion="Bogotá"
            )
            db.add(cliente)
            db.flush()
            finca = FincaModel(
                id_cliente=cliente.id_cliente,
                nombre_finca="Finca El Paraíso",
                ubicacion_municipio="Yopal, Casanare",
                hectareas=120.0, latitud=5.3378, longitud=-72.3947
            )
            db.add(finca)
            db.commit()
            db.refresh(cliente)
            db.refresh(finca)
            print(f"  ✅ Demo client seeded: {test_client_email} / cliente123")
        else:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == test_user.id_usuarios).first()
            finca = db.query(FincaModel).filter(FincaModel.id_cliente == cliente.id_cliente).first() if cliente else None
            print(f"  ℹ Demo client already exists")

        # Get tecnico + servicios for agenda seeding
        tecnico = db.query(TecnicoModel).first()
        servicio = db.query(ServicioModel).first()
        drone = db.query(DroneModel).filter(DroneModel.estado != "mantenimiento").first()

        # Seed agenda turnos if none exist
        existing_agenda = db.query(AgendaModel).count()
        if existing_agenda == 0 and tecnico and servicio and cliente and finca:
            today = date.today()
            turnos = [
                {"id_servicio": servicio.id_servicio,
                 "id_finca": finca.id_finca, "id_tecnico": tecnico.id_tecnico,
                 "id_drone": drone.id_drone if drone else None,
                 "fecha_de_turno": today + timedelta(days=1), "hora_inicio_estimada": "08:00:00",
                 "hora_fin_estimada": "10:00:00", "tipo_turno": "Fumigación",
                 "estado": "Confirmado", "tarifa": 350000, "cel": cliente.telefono, "observaciones_servicio": "Turno de prueba"},
                {"id_servicio": servicio.id_servicio,
                 "id_finca": finca.id_finca, "id_tecnico": None, "id_drone": None,
                 "fecha_de_turno": today + timedelta(days=3), "hora_inicio_estimada": "10:00:00",
                 "hora_fin_estimada": "11:00:00", "tipo_turno": "Fumigación",
                 "estado": "Pendiente", "tarifa": 210000, "cel": cliente.telefono, "observaciones_servicio": "Requiere asignación de técnico"},
            ]
            for t in turnos:
                db.add(AgendaModel(**t))
            db.commit()
            print(f"  ✅ Seeded {len(turnos)} agenda turnos")
        else:
            print(f"  ℹ {existing_agenda} agenda records exist")

        # Seed pagos for completed turnos
        completed_turnos = db.query(AgendaModel).filter(AgendaModel.estado == "Completado").all()
        if completed_turnos:
            for turno in completed_turnos:
                pago_exists = db.query(PagoModel).filter(PagoModel.id_turno == turno.id_turno).first()
                if not pago_exists:
                    db.add(PagoModel(
                        id_turno=turno.id_turno, id_cliente=turno.id_cliente,
                        monto=turno.precio_total or 350000,
                        metodo_pago="Transferencia", estado="verificado"
                    ))
            db.commit()
            print(f"  ✅ Pagos seeded for completed turnos")

        db.close()
        print("── SEED COMPLETE ─────────────────────────────────────────\n")
    except Exception as e:
        db.rollback()
        db.close()
        print(f"  ❌ SEED ERROR: {e}")
        import traceback; traceback.print_exc()

# ── API VERIFICATION ───────────────────────────────────────────────────────
def verify_all():
    print("\n── VERIFYING ALL API ENDPOINTS ───────────────────────────")

    # 1. Login Tests
    print("\n[AUTH]")
    admin_token = get_token("admin@flymetrics.co", "admin123")
    log(bool(admin_token), "Admin login → admin@flymetrics.co / admin123")

    tech_token = get_token("tecnico@flymetrics.co", "tecnico123")
    log(bool(tech_token), "Técnico login → tecnico@flymetrics.co / tecnico123")

    client_token = get_token("cliente.demo@flymetrics.co", "cliente123")
    log(bool(client_token), "Cliente login → cliente.demo@flymetrics.co / cliente123")

    if not admin_token:
        print("  ⚠ Cannot continue without admin token")
        return

    # 2. Auth me
    code, body = api("GET", "/auth/me", admin_token)
    log(code == 200, f"/auth/me → rol={body.get('data', {}).get('rol', 'N/A')}")

    # 3. Usuarios admin
    print("\n[ADMIN: USUARIOS]")
    code, body = api("GET", "/admin/usuarios", admin_token)
    users = body.get("data", [])
    log(code == 200, f"/admin/usuarios → {len(users)} usuarios encontrados")
    roles_found = set(u.get("rol") for u in users)
    log("administrador" in roles_found and "tecnico" in roles_found, f"Roles encontrados: {roles_found}")

    # 4. Servicios
    print("\n[SERVICIOS]")
    code, body = api("GET", "/servicios")
    servicios = body.get("data", [])
    log(code == 200, f"/servicios → {len(servicios)} servicios")

    # Create a service as admin
    code, body = api("POST", "/servicios", admin_token, {
        "nombre_servicio": "Servicio de Prueba Verificación",
        "descripcion": "Servicio creado por verificación automática",
        "precio_base_m2": 0.99, "activo": True
    })
    new_srv_id = body.get("data", {}).get("id_servicio") or body.get("data", {}).get("id")
    log(code in (200, 201), f"POST /servicios → id={new_srv_id}")

    if new_srv_id:
        code2, _ = api("DELETE", f"/servicios/{new_srv_id}", admin_token)
        log(code2 in (200, 204), f"DELETE /servicios/{new_srv_id}")

    # 5. Drones
    print("\n[DRONES]")
    code, body = api("GET", "/drones", admin_token)
    drones = body.get("data", [])
    log(code == 200, f"/drones → {len(drones)} drones")

    # Create drone
    code, body = api("POST", "/drones", admin_token, {
        "modelo": "Drone Verificación Test",
        "numero_serie": "VERIFY-001",
        "estado": "disponible",
        "tipo": "Prueba"
    })
    drone_id = body.get("data", {}).get("id_drone") or body.get("data", {}).get("id")
    log(code in (200, 201), f"POST /drones (crear) → id={drone_id}")

    if drone_id:
        code2, body2 = api("PUT", f"/drones/{drone_id}", admin_token, {"estado": "mantenimiento"})
        log(code2 == 200, f"PUT /drones/{drone_id} (actualizar estado)")
        code3, _ = api("DELETE", f"/drones/{drone_id}", admin_token)
        log(code3 in (200, 204), f"DELETE /drones/{drone_id}")

    # 6. Tecnicos
    print("\n[TECNICOS]")
    code, body = api("GET", "/tecnicos", admin_token)
    tecnicos = body.get("data", [])
    log(code == 200, f"/tecnicos → {len(tecnicos)} técnicos")

    # 7. Clientes
    print("\n[CLIENTES]")
    code, body = api("GET", "/clientes", admin_token)
    clientes_list = body.get("data", [])
    log(code == 200, f"/clientes → {len(clientes_list)} clientes")

    # 8. Fincas (cliente)
    print("\n[FINCAS]")
    if client_token:
        code, body = api("GET", "/fincas", client_token)
        fincas = body.get("data", [])
        log(code == 200, f"/fincas (cliente) → {len(fincas)} fincas")
        # Admin verifying fincas
        code2, body2 = api("GET", "/fincas", admin_token)
        log(code2 == 200, f"/fincas (admin) → {len(body2.get('data',[]))} fincas")

    # 9. Agenda
    print("\n[AGENDA]")
    code, body = api("GET", "/admin/agenda", admin_token)
    turnos = body.get("data", [])
    log(code == 200, f"/admin/agenda → {len(turnos)} turnos")

    code2, body2 = api("GET", "/tecnico/agenda", tech_token)
    log(code2 == 200, f"/tecnico/agenda → {len(body2.get('data', []))} turnos para técnico")

    # 10. Pagos
    print("\n[PAGOS]")
    code, body = api("GET", "/admin/pagos", admin_token)
    pagos = body.get("data", [])
    log(code == 200, f"/admin/pagos → {len(pagos)} pagos")

    # 11. Reportes vuelo
    print("\n[REPORTES]")
    code, body = api("GET", "/reportes-vuelo", admin_token)
    log(code == 200, f"/reportes-vuelo → {len(body.get('data', []))} reportes")

    # 12. Notificaciones
    print("\n[NOTIFICACIONES]")
    if client_token:
        code, body = api("GET", "/notificaciones", client_token)
        log(code == 200, f"/notificaciones (cliente) → {len(body.get('data', []))} notificaciones")

    # 13. Entregables
    print("\n[ENTREGABLES]")
    if client_token:
        code, body = api("GET", "/entregables/mis-archivos", client_token)
        log(code == 200, f"/entregables/mis-archivos → {len(body.get('data', []))} archivos")

    # Final summary
    passed = sum(1 for s, _ in RESULTS if s)
    total = len(RESULTS)
    print(f"\n{'─'*55}")
    print(f"RESULTADO: {passed}/{total} checks pasados")
    if passed < total:
        print("\nChecks fallidos:")
        for s, m in RESULTS:
            if not s:
                print(f"  ❌ {m}")
    print('─'*55)

if __name__ == "__main__":
    seed_all()
    verify_all()
