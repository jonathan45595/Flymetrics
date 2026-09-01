"""
Flymetrics - Corrected Seed Script with proper field names from models.py
"""
import sys, os
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))
os.chdir(str(base_dir))

from datetime import date, timedelta
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, TecnicoModel, DroneModel,
    ServicioModel, FincaModel, AgendaModel, PagoModel, TipoTurnoEnum, MetodoPagoEnum
)
from app.infrastructure.security.jwt_handler import hash_password

def seed():
    db = SessionLocal()
    try:
        print("[SEED] Starting...")

        # 1. Servicios - field is precio_base_m2
        # Convert price per ha to price per m2 (1 ha = 10000 m2)
        servicios_data = [
            {"nombre_servicio": "Fumigacion aerea", "descripcion": "Aplicacion de agroquimicos con sistema de aspersion de precision.", "precio_base_m2": 0.70},
            {"nombre_servicio": "Fertilizacion", "descripcion": "Distribucion aerea de fertilizantes solidos o liquidos.", "precio_base_m2": 0.70},
            {"nombre_servicio": "Mapeo topografico", "descripcion": "Generacion de mapas NDVI y modelos 3D del terreno.", "precio_base_m2": 0.60},
            {"nombre_servicio": "Inspeccion de cultivos", "descripcion": "Revision visual y analisis multiespectral de cultivos.", "precio_base_m2": 0.50},
        ]
        existing_srv = db.query(ServicioModel).count()
        if existing_srv == 0:
            for s in servicios_data:
                db.add(ServicioModel(**s))
            db.commit()
            print(f"  [+] Seeded {len(servicios_data)} services")
        else:
            print(f"  [i] {existing_srv} services already exist")

        # 2. Drones - ultima_revision is String(50) not Date
        drones_data = [
            {"modelo": "Sistema de Aspersion de Precision", "numero_serie": "AGT40-001", "estado": "disponible", "horas_vuelo": 420, "tipo": "aspersion", "ultima_revision": "2026-05-15"},
            {"modelo": "Sistema Multiespectral Beta", "numero_serie": "M3E-002", "estado": "disponible", "horas_vuelo": 180, "tipo": "fotogrametria", "ultima_revision": "2026-05-20"},
            {"modelo": "Sistema de Fertilizacion", "numero_serie": "AGT10-003", "estado": "mantenimiento", "horas_vuelo": 650, "tipo": "aspersion", "ultima_revision": "2026-04-10"},
        ]
        existing_drones = db.query(DroneModel).count()
        if existing_drones == 0:
            for d in drones_data:
                db.add(DroneModel(**d))
            db.commit()
            print(f"  [+] Seeded {len(drones_data)} drones")
        else:
            print(f"  [i] {existing_drones} drones already exist")

        # 3. Demo client user + profile + finca
        # FincaModel fields: ubicacion_municipio (not municipio/departamento)
        test_client_email = "cliente.demo@flymetrics.co"
        test_user = db.query(UsuarioModel).filter(UsuarioModel.email == test_client_email).first()
        if not test_user:
            test_user = UsuarioModel(email=test_client_email, contraseña=hash_password("cliente123"), rol="cliente")
            db.add(test_user)
            db.flush()
            cliente = ClienteModel(
                id_usuario=test_user.id_usuarios,
                nombre="Carlos", apellido_1="Mendoza", apellido_2="Ortiz",
                telefono="3001234567", verificado=True, ciudad_expedicion="Bogota"
            )
            db.add(cliente)
            db.flush()
            # FincaModel: uses ubicacion_municipio, NOT municipio/departamento
            finca = FincaModel(
                id_cliente=cliente.id_cliente,
                nombre_finca="Finca El Paraiso",
                ubicacion_municipio="Yopal, Casanare",
                hectareas=120.0, latitud=5.3378, longitud=-72.3947
            )
            db.add(finca)
            db.commit()
            db.refresh(cliente)
            db.refresh(finca)
            print(f"  [+] Demo client seeded: {test_client_email} / cliente123")
        else:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == test_user.id_usuarios).first()
            finca = db.query(FincaModel).filter(FincaModel.id_cliente == cliente.id_cliente).first() if cliente else None
            print(f"  [i] Demo client already exists: {test_client_email}")

        # 4. Seed agenda turnos
        tecnico = db.query(TecnicoModel).first()
        servicio = db.query(ServicioModel).first()
        drone = db.query(DroneModel).filter(DroneModel.estado == "disponible").first()

        existing_agenda = db.query(AgendaModel).count()
        if existing_agenda == 0 and tecnico and servicio and cliente and finca:
            today = date.today()
            # AgendaModel fields: fecha_de_turno, hora_inicio_estimada, tipo_turno (Enum), estado, tarifa
            turnos = [
                {
                    "id_finca": finca.id_finca, "id_servicio": servicio.id_servicio,
                    "id_tecnico": tecnico.id_tecnico, "id_drone": drone.id_drone if drone else None,
                    "fecha_de_turno": today + timedelta(days=1), "hora_inicio_estimada": "08:00:00",
                    "tipo_turno": TipoTurnoEnum.Fumigacion,
                    "estado": "Confirmado", "tarifa": 840000.00,
                    "observaciones_servicio": "Aplicar en zona norte, cerca al rio."
                },
                {
                    "id_finca": finca.id_finca, "id_servicio": servicio.id_servicio,
                    "id_tecnico": None, "id_drone": None,
                    "fecha_de_turno": today + timedelta(days=3), "hora_inicio_estimada": "10:00:00",
                    "tipo_turno": TipoTurnoEnum.Fumigacion,
                    "estado": "Pendiente", "tarifa": 560000.00,
                    "observaciones_servicio": "Requiere asignacion de tecnico y dron."
                },
                {
                    "id_finca": finca.id_finca, "id_servicio": servicio.id_servicio,
                    "id_tecnico": tecnico.id_tecnico, "id_drone": drone.id_drone if drone else None,
                    "fecha_de_turno": today - timedelta(days=2), "hora_inicio_estimada": "07:00:00",
                    "tipo_turno": TipoTurnoEnum.Fumigacion,
                    "estado": "Hecho", "tarifa": 700000.00,
                    "observaciones_servicio": "Completado sin incidentes."
                },
            ]
            for t in turnos:
                db.add(AgendaModel(**t))
            db.commit()
            print(f"  [+] Seeded {len(turnos)} agenda turnos")

            # Seed a pago for the completed turno
            turno_hecho = db.query(AgendaModel).filter(AgendaModel.estado == "Hecho").first()
            if turno_hecho:
                db.add(PagoModel(
                    id_turno=turno_hecho.id_turno,
                    monto=700000.00,
                    metodo_pago=MetodoPagoEnum.Transferencia,
                    referencia_transaccion="TRF-20260717-001"
                ))
                db.commit()
                print(f"  [+] Pago seeded for completed turno")
        else:
            print(f"  [i] {existing_agenda} agenda records exist - skipping")

        print("[SEED] COMPLETE!")
    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR] {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
