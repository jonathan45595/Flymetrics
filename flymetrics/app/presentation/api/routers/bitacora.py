from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import BitacoraUseCases
from app.presentation.api.dependencies.auth import get_current_user, RoleChecker
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="", tags=["Bitácora del Técnico & Vuelo"])

tecnico_required = RoleChecker(["tecnico", "administrador"])

@router.get("/tecnico/agenda")
def get_tecnico_agenda(
    fecha: date = Query(None, description="Fecha YYYY-MM-DD. Por defecto es hoy."),
    estado: str = Query(None, description="Filtrar por: Pendiente, Confirmado, En Proceso"),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(tecnico_required)
):
    """Retorna los turnos asignados al técnico autenticado para la fecha solicitada."""
    turnos = BitacoraUseCases.get_tecnico_agenda(db, current_user, fecha, estado)
    data = []
    for t in turnos:
        item = {
            "id_turno": t.id_turno,
            "id_finca": t.id_finca,
            "id_servicio": t.id_servicio,
            "id_drone": t.id_drone,
            "id_tecnico": t.id_tecnico,
            "fecha_de_turno": t.fecha_de_turno.isoformat() if t.fecha_de_turno else None,
            "hora_inicio_estimada": str(t.hora_inicio_estimada) if t.hora_inicio_estimada else "10:00:00",
            "hora_fin_estimada": str(t.hora_fin_estimada) if t.hora_fin_estimada else "12:00:00",
            "tipo_turno": t.tipo_turno.value if hasattr(t.tipo_turno, 'value') else str(t.tipo_turno or 'Fumigación'),
            "estado": t.estado or "Pendiente",
            "tarifa": float(t.tarifa or 0.0),
            "costo_logistico": float(t.costo_logistico or 0.0),
            "observaciones_servicio": t.observaciones_servicio or "",
            "notas": t.observaciones_servicio or ""
        }
        # Extraer cultivo, notas adicionales del cliente y detalles reales desde observaciones
        obs_text = t.observaciones_servicio or ""
        import re
        m_cul = re.search(r'(?:Cultivo y Area|Cultivo):\s*([^\(\n\r]+)', obs_text, re.IGNORECASE)
        cultivo_real = m_cul.group(1).strip() if m_cul else "Agrícola"

        m_ver = re.search(r'(?:Vereda / Corregimiento|Vereda):\s*([^\n\r]+)', obs_text, re.IGNORECASE)
        vereda_real = m_ver.group(1).strip() if m_ver else ""

        m_dir = re.search(r'(?:Direccion / Coordenadas|Dirección|Ubicación):\s*([^\n\r]+)', obs_text, re.IGNORECASE)
        dir_real = m_dir.group(1).strip() if m_dir else ""

        m_cli_notas = re.search(r'(?:Notas Adicionales|Observaciones Adicionales):\s*([^\n\r]+(?:\n[^\n\r\-•]+)*)', obs_text, re.IGNORECASE)
        notas_cliente = m_cli_notas.group(1).strip() if m_cli_notas else ""

        item["tipo_cultivo"] = cultivo_real
        item["cultivo"] = cultivo_real
        item["notas_cliente"] = notas_cliente
        item["motivo_reagendamiento"] = t.motivo_reagendamiento or ""

        if t.finca:
            item["id_finca"] = t.finca.id_finca
            item["finca_nombre"] = t.finca.nombre_finca
            item["ubicacion_municipio"] = t.finca.ubicacion_municipio or "Colombia"
            item["departamento"] = t.finca.departamento or ""
            item["hectareas"] = float(t.finca.hectareas or 10.0)
            item["latitud"] = float(t.finca.latitud) if t.finca.latitud is not None else None
            item["longitud"] = float(t.finca.longitud) if t.finca.longitud is not None else None
            item["maps_url"] = getattr(t.finca, 'maps_url', None) or getattr(t.finca, 'url_maps', None) or (f"https://www.google.com/maps?q={t.finca.latitud},{t.finca.longitud}" if t.finca.latitud is not None and t.finca.longitud is not None else "")
            if t.finca.latitud is not None and t.finca.longitud is not None:
                item["coordenadas"] = f"{t.finca.latitud}, {t.finca.longitud}"
            elif dir_real and dir_real != "N/A":
                item["coordenadas"] = f"{dir_real} ({t.finca.ubicacion_municipio or ''} {t.finca.departamento or ''})".strip()
            else:
                loc_parts = [vereda_real, t.finca.ubicacion_municipio, t.finca.departamento]
                item["coordenadas"] = ", ".join([p for p in loc_parts if p]) or "Colombia"

            if t.finca.cliente:
                c = t.finca.cliente
                item["id_cliente"] = c.id_cliente
                apellidos = f"{c.apellido_1 or ''} {c.apellido_2 or ''}".strip()
                item["cliente_nombre"] = f"{c.nombre} {apellidos}".strip()
                item["cliente_telefono"] = c.telefono or ""
                item["cliente_cedula"] = c.numero_documento or ""
                if c.usuario:
                    item["cliente_email"] = c.usuario.email
                else:
                    item["cliente_email"] = ""
            else:
                item["id_cliente"] = None
                item["cliente_nombre"] = "Sin cliente asociado"
                item["cliente_telefono"] = ""
                item["cliente_email"] = ""
                item["cliente_cedula"] = ""
        else:
            item["id_finca"] = None
            item["finca_nombre"] = "Finca no asignada"
            item["ubicacion_municipio"] = "Colombia"
            item["departamento"] = ""
            item["hectareas"] = 10.0
            item["latitud"] = None
            item["longitud"] = None
            item["coordenadas"] = "Colombia"
            item["id_cliente"] = None
            item["cliente_nombre"] = "Sin cliente asociado"
            item["cliente_telefono"] = ""
            item["cliente_email"] = ""
            item["cliente_cedula"] = ""

        if t.servicio:
            item["servicio_nombre"] = t.servicio.nombre_servicio
            item["servicio_descripcion"] = t.servicio.descripcion or ""
        else:
            item["servicio_nombre"] = "Servicio Agrícola Dron"
            item["servicio_descripcion"] = ""

        if t.drone:
            item["dron_nombre"] = f"{t.drone.modelo} ({t.drone.matricula})" if hasattr(t.drone, 'matricula') and t.drone.matricula else t.drone.modelo
        else:
            item["dron_nombre"] = "Flota General Flymetrics"

        data.append(item)

    return success_response(message="Agenda del técnico obtenida exitosamente", data=data)

@router.patch("/tecnico/agenda/{id_turno}/decision")
def registrar_decision(
    id_turno: int,
    request: schemas.AgendaDecisionRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(tecnico_required)
):
    """El técnico confirma (true) o rechaza (false) un turno asignado. Requiere justificación al rechazar."""
    turno = BitacoraUseCases.registrar_decision(db, id_turno, request, current_user)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message=f"Decisión registrada. Estado del turno: {turno.estado}", data=data)

@router.patch("/tecnico/agenda/{id_turno}/checkin")
def checkin(
    id_turno: int,
    request: schemas.CheckinRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(tecnico_required)
):
    """El técnico registra la hora de llegada al terreno. Estado del turno -> 'En Proceso'."""
    turno = BitacoraUseCases.checkin(db, id_turno, request, current_user)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Check-in registrado. Turno en proceso.", data=data)

@router.patch("/tecnico/agenda/{id_turno}/checkout")
def checkout(
    id_turno: int,
    request: schemas.CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(tecnico_required)
):
    """El técnico cierra el turno y llena el reporte RAC 100 de la Aerocivil. Crea registro en tabla_reportes_vuelo."""
    reporte = BitacoraUseCases.checkout(db, id_turno, request, current_user)
    data = schemas.ReporteVueloResponse.model_validate(reporte).model_dump()
    return success_response(message="Checkout registrado y bitácora guardada. Turno completado.", data=data)

@router.get("/reportes-vuelo")
def list_reportes(
    id_turno: int = Query(None),
    id_tecnico: int = Query(None, description="Filtrar por técnico (solo admin)."),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Lista todos los reportes de vuelo. Admin ve todos, técnico solo los suyos."""
    reportes = BitacoraUseCases.list_reportes(db, current_user, id_turno, id_tecnico)
    data = []
    for r in reportes:
        item = {
            "id_reporte": r.id_reporte,
            "id_bitacora": r.id_reporte,
            "id_turno": r.id_turno,
            "insumos_litros_aplicados": float(r.insumos_litros_aplicados or 15.0),
            "agua_litros": float(r.agua_litros or 100.0),
            "baterias_utilizadas": r.baterias_utilizadas or 4,
            "cumple_rac100": r.cumple_rac100 if r.cumple_rac100 is not None else 1,
            "url_entregable_drive": r.url_entregable_drive,
            "recomendaciones_agronomicas": r.recomendaciones_agronomicas,
            "observaciones_campo": r.observaciones_campo or "Operación ejecutada bajo parámetros RAC-100."
        }
        if r.turno:
            item["fecha"] = (r.turno.fecha_de_turno or r.created_at).isoformat() if (r.turno.fecha_de_turno or r.created_at) else ""
            item["duracion_min"] = 45
            item["area_ha"] = float(r.turno.finca.hectareas or 10.0) if (r.turno.finca and r.turno.finca.hectareas) else 10.0
            
            if r.turno.finca:
                item["finca"] = r.turno.finca.nombre_finca
                if r.turno.finca.cliente:
                    c = r.turno.finca.cliente
                    item["cliente"] = f"{c.nombre} {c.apellido_1 or ''}".strip()
                else:
                    item["cliente"] = "Cliente Flymetrics"
            else:
                item["finca"] = "Finca Registrada"
                item["cliente"] = "Cliente Flymetrics"

            if r.turno.servicio:
                item["servicio"] = r.turno.servicio.nombre_servicio
            else:
                item["servicio"] = "Vuelo Agrícola"

            if r.turno.tecnico and r.turno.tecnico.usuario:
                item["tecnico"] = r.turno.tecnico.usuario.email.split('@')[0]
            else:
                item["tecnico"] = "Piloto Certificado"
        else:
            item["fecha"] = r.created_at.isoformat() if r.created_at else ""
            item["cliente"] = "Cliente Flymetrics"
            item["finca"] = "Finca Registrada"
            item["servicio"] = "Vuelo Agrícola"
            item["tecnico"] = "Piloto Certificado"
            item["duracion_min"] = 45
            item["area_ha"] = 10.0

        data.append(item)

    return success_response(message="Lista de reportes de vuelo obtenida exitosamente", data=data)
