import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.database.session import SessionLocal, engine
from app.infrastructure.database.models.models import (
    Base, UsuarioModel, ClienteModel, TecnicoModel, FincaModel, ServicioModel,
    AgendaModel, DroneModel, PagoModel, ReporteVueloModel, EntregableModel, PQRModel
)
from app.infrastructure.security.jwt_handler import hash_password
from datetime import datetime, date, time

def clean_and_seed():
    db = SessionLocal()
    try:
        print("[CLEAN] Limpiando registros antiguos de la base de datos...")
        
        # Clear tables in reverse dependency order
        db.query(EntregableModel).delete()
        db.query(ReporteVueloModel).delete()
        db.query(PagoModel).delete()
        db.query(AgendaModel).delete()
        db.query(FincaModel).delete()
        db.query(PQRModel).delete()
        db.query(DroneModel).delete()
        db.query(TecnicoModel).delete()
        db.query(ClienteModel).delete()
        db.query(ServicioModel).delete()
        db.query(UsuarioModel).delete()
        db.commit()

        print("[SEED] Sembrando usuarios principales de demostracion...")

        # 1. Admin
        u_admin = UsuarioModel(
            email="admin@flymetrics.co",
            contraseña=hash_password("Admin#1234"),
            rol="administrador"
        )
        db.add(u_admin)

        # 2. Técnico
        u_tech = UsuarioModel(
            email="tecnico@flymetrics.co",
            contraseña=hash_password("Tecnico#1234"),
            rol="tecnico"
        )
        db.add(u_tech)

        # 3. Cliente
        u_cli = UsuarioModel(
            email="cliente@flymetrics.co",
            contraseña=hash_password("cliente123"),
            rol="cliente"
        )
        db.add(u_cli)
        db.flush()

        # Profiles
        t_tech = TecnicoModel(
            id_usuario=u_tech.id_usuarios,
            nombre="Juan",
            apellido_1="Perez",
            certificacion="Piloto RPAS Nivel A - RAC-100",
            estado="disponible",
            telefono="3001234567"
        )
        db.add(t_tech)

        c_cli = ClienteModel(
            id_usuario=u_cli.id_usuarios,
            nombre="Miguel",
            apellido_1="Prada",
            telefono="3054061764",
            numero_documento="1020304050",
            fecha_expedicion="2018-05-15",
            verificado=True
        )
        db.add(c_cli)
        db.flush()

        print("[SEED] Creando fincas y catalogo de servicios...")
        
        f1 = FincaModel(
            id_cliente=c_cli.id_cliente,
            nombre_finca="Finca El Prado",
            ubicacion_municipio="Palmira, Valle del Cauca",
            hectareas=25.0,
            latitud=3.5394,
            longitud=-76.3036
        )
        f2 = FincaModel(
            id_cliente=c_cli.id_cliente,
            nombre_finca="Hacienda La Palma",
            ubicacion_municipio="Villavicencio, Meta",
            hectareas=40.0,
            latitud=4.1420,
            longitud=-73.6266
        )
        db.add(f1)
        db.add(f2)

        s1 = ServicioModel(
            nombre_servicio="Fumigacion y Aspersion Agricola con Dron",
            descripcion="Aplicacion automatizada de insumos foliares con ultra bajo volumen y telemetria RAC-100.",
            precio_base_m2=50.0,
            activo=True
        )
        s2 = ServicioModel(
            nombre_servicio="Fotogrametria y Salud de Cultivo NDVI",
            descripcion="Mapeo multiespectral de alta resolucion para diagnostico de nitrogeno y estres hidrico.",
            precio_base_m2=35.0,
            activo=True
        )
        db.add(s1)
        db.add(s2)

        d1 = DroneModel(
            modelo="DJI Agras T40",
            estado="disponible",
            tipo="aspersion",
            numero_serie="SN-T40-90123",
            horas_vuelo=120,
            id_tecnico_asignado=t_tech.id_tecnico
        )
        d2 = DroneModel(
            modelo="Mavic 3 Multispectral",
            estado="disponible",
            tipo="fotogrametria",
            numero_serie="SN-M3M-45678",
            horas_vuelo=65,
            id_tecnico_asignado=t_tech.id_tecnico
        )
        db.add(d1)
        db.add(d2)
        db.flush()

        print("[SEED] Agendando vuelos de prueba...")

        turn1 = AgendaModel(
            id_finca=f1.id_finca,
            id_servicio=s1.id_servicio,
            id_tecnico=t_tech.id_tecnico,
            id_drone=d1.id_drone,
            fecha_de_turno=date(2026, 8, 14),
            hora_inicio_estimada=time(10, 0),
            hora_fin_estimada=time(12, 0),
            estado="Hecho",
            tarifa=1250000.0,
            observaciones_servicio="Aplicacion foliar en zona norte de Cana."
        )
        turn2 = AgendaModel(
            id_finca=f2.id_finca,
            id_servicio=s2.id_servicio,
            id_tecnico=t_tech.id_tecnico,
            id_drone=d2.id_drone,
            fecha_de_turno=date(2026, 8, 20),
            hora_inicio_estimada=time(8, 0),
            hora_fin_estimada=time(11, 0),
            estado="Confirmado",
            tarifa=950000.0,
            observaciones_servicio="Mapeo multiespectral NDVI completo."
        )
        db.add(turn1)
        db.add(turn2)
        db.flush()

        print("[SEED] Registrando facturacion y comprobantes...")

        pag1 = PagoModel(
            id_turno=turn1.id_turno,
            monto=1250000.0,
            metodo_pago="Transferencia",
            referencia_transaccion="REF-BC-901284",
            url_cotizacion="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            url_comprobante="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            estado_pago="Pagado"
        )
        pag2 = PagoModel(
            id_turno=turn2.id_turno,
            monto=950000.0,
            metodo_pago="Transferencia",
            referencia_transaccion="REF-NQ-458129",
            url_cotizacion="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            estado_pago="Pendiente"
        )
        db.add(pag1)
        db.add(pag2)

        bit1 = ReporteVueloModel(
            id_turno=turn1.id_turno,
            insumos_litros_aplicados=45.0,
            agua_litros=300.0,
            baterias_utilizadas=6,
            cumple_rac100=1,
            observaciones_campo="Vuelo ejecutado bajo norma RAC-100 sin contratiempos.",
            url_entregable_drive="https://drive.google.com",
            recomendaciones_agronomicas="Repetir monitoreo NDVI en 15 dias."
        )
        db.add(bit1)

        ent1 = EntregableModel(
            id_turno=turn1.id_turno,
            tipo_archivo="reporte_pdf",
            url_archivo="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            nombre_archivo="Reporte_Tecnico_Fumigacion_FM1.pdf"
        )
        db.add(ent1)

        db.commit()
        print("[SUCCESS] Base de datos reseteada y sembrada al 100% exitosamente!")

    except Exception as e:
        db.rollback()
        print("[ERROR] Error al limpiar y sembrar base de datos:", e)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_seed()
