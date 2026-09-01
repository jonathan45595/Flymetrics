from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import AgendaUseCases
from app.presentation.api.dependencies.auth import get_current_user, RoleChecker
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/agenda", tags=["Agendamiento y Reservas"])

# Dependencias de roles
cliente_or_admin = RoleChecker(["cliente", "administrador"])
admin_required = RoleChecker(["administrador"])

@router.post("/reserva-rapida", status_code=status.HTTP_201_CREATED)
def crear_reserva_rapida_publica(request: schemas.ReservaRapidaCreate, db: Session = Depends(get_db)):
    """Endpoint público (sin autenticación previa) para agendamiento directo de vuelos agrícolas por parte de finqueros."""
    resultado = AgendaUseCases.crear_reserva_rapida(db, request)
    return success_response(message=resultado["mensaje"], data=resultado, status_code=201)

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/reservar", status_code=status.HTTP_201_CREATED)
def create_reserva(request: schemas.AgendaCreate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(cliente_or_admin)):
    """Crea un turno de agendamiento (Cliente o Administrador)."""
    turno = AgendaUseCases.create_turno(db, request, current_user)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Solicitud de reserva creada exitosamente", data=data, status_code=201)

@router.get("/mis-turnos")
def get_mis_turnos(
    estado: str = Query(None, description="Filtrar por estado: Pendiente, Confirmado, En Proceso, Hecho, Cancelado"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(cliente_or_admin)
):
    """Retorna todos los turnos del cliente autenticado con nombres enriquecidos."""
    turnos = AgendaUseCases.list_mis_turnos(db, current_user, estado, page, limit)
    data = []
    for t in turnos:
        item = schemas.AgendaResponse.model_validate(t).model_dump()
        if t.finca:
            item["finca_nombre"] = t.finca.nombre_finca
            item["nombre_finca"] = t.finca.nombre_finca
        else:
            item["finca_nombre"] = "Finca Registrada"
            item["nombre_finca"] = "Finca Registrada"
            
        obs_raw = t.observaciones_servicio or ""
        import re
        m_svc = re.search(r'\[Servicios:\s*([^\]]+)\]', obs_raw, re.IGNORECASE)
        if m_svc:
            item["servicio_nombre"] = m_svc.group(1).strip()
            item["nombre_servicio"] = m_svc.group(1).strip()
        elif t.servicio:
            item["servicio_nombre"] = t.servicio.nombre_servicio
            item["nombre_servicio"] = t.servicio.nombre_servicio
        else:
            item["servicio_nombre"] = "Servicio Dron"
            item["nombre_servicio"] = "Servicio Dron"
            
        if t.tecnico:
            item["tecnico_nombre"] = f"{t.tecnico.nombre} {t.tecnico.apellido_1 or ''}".strip()
            item["tecnico"] = f"{t.tecnico.nombre} {t.tecnico.apellido_1 or ''}".strip()
        else:
            item["tecnico_nombre"] = "Por asignar"
            item["tecnico"] = "Por asignar"
            
        data.append(item)
    return success_response(message="Lista de turnos del cliente obtenida", data=data)

@router.get("/estado/{id_turno}")
def get_estado_publico(id_turno: int, db: Session = Depends(get_db)):
    """Consulta de estado pública para uso del chatbot de WhatsApp."""
    result = AgendaUseCases.get_estado_publico(db, id_turno)
    return success_response(message="Estado del turno obtenido", data=result)

@router.get("/{id_turno}")
def get_turno(id_turno: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Retorna el detalle completo de un turno (técnico asignado, dron, tiempos estimados y reales)."""
    turno = AgendaUseCases.get_by_id(db, id_turno, current_user)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Detalle del turno obtenido exitosamente", data=data)

@router.delete("/{id_turno}")
def cancelar_turno(id_turno: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """El cliente cancela su reserva. Solo se permite en estado 'Pendiente' o 'Confirmado'."""
    AgendaUseCases.cancelar_turno(db, id_turno, current_user)
    return success_response(message="Turno cancelado exitosamente")

@router.put("/{id_turno}")
@router.patch("/{id_turno}")
def update_turno(
    id_turno: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Actualiza la fecha de muestreo, estado u observaciones de un turno agendado."""
    from app.infrastructure.database.models.models import AgendaModel
    from app.shared.exceptions.exceptions import NotFoundException
    turno = db.query(AgendaModel).filter(AgendaModel.id_turno == id_turno).first()
    if not turno:
        raise NotFoundException("Turno no encontrado")
    
    # 1. Fecha de turno / fecha
    new_fecha_val = request.get("fecha_de_turno") or request.get("fecha") or request.get("nueva_fecha")
    if new_fecha_val:
        if isinstance(new_fecha_val, str):
            new_date = datetime.strptime(new_fecha_val.strip()[:10], "%Y-%m-%d").date()
        else:
            new_date = new_fecha_val
        if current_user.rol != "administrador" and new_date < date.today():
            from app.shared.exceptions.exceptions import BadRequestException
            raise BadRequestException("No es posible reprogramar un turno para fechas anteriores a hoy.")
        turno.fecha_de_turno = new_date

    # 2. Hora de inicio estimada / hora
    new_hora_val = request.get("hora_inicio_estimada") or request.get("hora") or request.get("nueva_hora")
    if new_hora_val:
        from datetime import time as time_cls, timedelta
        if isinstance(new_hora_val, str):
            parts = new_hora_val.strip().split(":")
            h_obj = time_cls(int(parts[0]), int(parts[1]))
        else:
            h_obj = new_hora_val
        turno.hora_inicio_estimada = h_obj

        # Recalcular hora_fin_estimada según hectáreas
        ha = float(turno.finca.hectareas or 10.0) if turno.finca else 10.0
        dur_horas = max(1.0, round(ha / 5.0, 1))
        base_d = turno.fecha_de_turno or date.today()
        st_dt = datetime.combine(base_d, h_obj)
        end_dt = st_dt + timedelta(hours=dur_horas)
        turno.hora_fin_estimada = end_dt.time()

    # 3. Motivo de Reagendamiento (Campo independiente en BD)
    new_motivo = request.get("motivo_reagendamiento") or request.get("motivo") or request.get("motivo_cambio")
    if new_motivo is not None and str(new_motivo).strip():
        turno.motivo_reagendamiento = str(new_motivo).strip()

    # 4. Observaciones generales (solo si se envían explícitamente y no son vacías)
    new_obs = request.get("observaciones_servicio")
    if new_obs is not None and str(new_obs).strip():
        turno.observaciones_servicio = str(new_obs).strip()

    # 5. Estado
    new_estado = request.get("estado")
    if new_estado:
        turno.estado = str(new_estado).strip()

    # 6. Recursos y llaves foráneas
    if "id_finca" in request and request["id_finca"]:
        turno.id_finca = int(request["id_finca"])
    if "id_servicio" in request and request["id_servicio"]:
        turno.id_servicio = int(request["id_servicio"])
    if "id_tecnico" in request and request["id_tecnico"]:
        turno.id_tecnico = int(request["id_tecnico"])
    if "id_drone" in request and request["id_drone"]:
        turno.id_drone = int(request["id_drone"])
    
    db.commit()
    db.refresh(turno)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Turno actualizado exitosamente", data=data)


@router.get("")
def list_agenda_alias(
    estado: str = Query(None),
    id_tecnico: int = Query(None),
    fecha: date = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Alias para listar turnos de agenda sin error 404."""
    if current_user.rol == "cliente":
        turnos = AgendaUseCases.list_mis_turnos(db, current_user, estado)
    else:
        turnos = AgendaUseCases.list_all_admin(db, estado, id_tecnico, fecha)
        
    data = []
    for t in turnos:
        item = schemas.AgendaResponse.model_validate(t).model_dump()
        if t.finca:
            item["nombre_finca"] = t.finca.nombre_finca
        if t.servicio:
            item["nombre_servicio"] = t.servicio.nombre_servicio
        if t.tecnico:
            item["tecnico"] = f"{t.tecnico.nombre} {t.tecnico.apellido_1 or ''}".strip()
        data.append(item)
    return success_response(message="Lista de turnos obtenida", data=data)

# ==========================================
# RUTAS DE ADMINISTRADOR PARA AGENDA
# ==========================================

# Definimos las rutas de administrador de la agenda aquí
admin_router = APIRouter(prefix="/admin/agenda", tags=["Administración de Agenda"])

@admin_router.get("")
def admin_list_agenda(
    estado: str = Query(None),
    id_tecnico: int = Query(None),
    fecha: date = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Vista completa de todos los turnos del sistema con nombres. Solo administrador."""
    turnos = AgendaUseCases.list_all_admin(db, estado, id_tecnico, fecha)
    data = []
    for t in turnos:
        item = schemas.AgendaResponse.model_validate(t).model_dump()
        # Enrich with names, email, phone and farm details
        if t.finca:
            item["finca_nombre"] = t.finca.nombre_finca
            item["hectareas"] = float(t.finca.hectareas) if t.finca.hectareas else 0.0
            if t.finca.cliente:
                item["cliente_nombre"] = f"{t.finca.cliente.nombre} {t.finca.cliente.apellido_1 or ''}".strip()
                item["cliente_telefono"] = t.finca.cliente.telefono or t.cel or ""
                item["cel"] = t.finca.cliente.telefono or t.cel or ""
                if t.finca.cliente.usuario:
                    item["cliente_email"] = t.finca.cliente.usuario.email or ""
                else:
                    item["cliente_email"] = ""
            else:
                item["cliente_nombre"] = ""
                item["cliente_telefono"] = t.cel or ""
                item["cliente_email"] = ""
        else:
            item["finca_nombre"] = ""
            item["cliente_nombre"] = ""
            item["cliente_email"] = ""
            item["cliente_telefono"] = t.cel or ""
            item["hectareas"] = 0.0

        # Multi-service name resolver
        obs_raw = t.observaciones_servicio or ""
        import re
        m_svc = re.search(r'\[Servicios:\s*([^\]]+)\]', obs_raw, re.IGNORECASE)
        if m_svc:
            item["servicio_nombre"] = m_svc.group(1).strip()
        elif t.servicio:
            item["servicio_nombre"] = t.servicio.nombre_servicio
        else:
            item["servicio_nombre"] = "Servicio Dron"

        if t.tecnico:
            item["tecnico_nombre"] = f"{t.tecnico.nombre} {t.tecnico.apellido_1 or ''}".strip()
        else:
            item["tecnico_nombre"] = ""
        item["motivo_reagendamiento"] = t.motivo_reagendamiento or ""
        data.append(item)
    return success_response(message="Historial completo de turnos obtenido por el administrador", data=data)

@admin_router.patch("/{id_turno}/estado")
def admin_force_estado(
    id_turno: int,
    request: schemas.AgendaForceEstadoRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """El administrador cambia manualmente el estado de cualquier turno."""
    turno = AgendaUseCases.force_estado_admin(db, id_turno, request)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Estado del turno forzado por el administrador exitosamente", data=data)

@admin_router.post("", status_code=status.HTTP_201_CREATED)
def admin_create_agenda(
    request: schemas.AgendaCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(RoleChecker(["administrador"]))
):
    """Permite al administrador crear un turno directamente en la agenda."""
    turno = AgendaUseCases.create_turno(db, request, current_user)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Turno creado exitosamente por el administrador", data=data, status_code=201)

@admin_router.patch("/{id_turno}/asignar")
def admin_asignar_recursos(
    id_turno: int,
    request: schemas.AgendaAsignarRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """El administrador asigna o reasigna el técnico y el dron para un turno."""
    turno = AgendaUseCases.asignar_tecnico_drone(db, id_turno, request)
    data = schemas.AgendaResponse.model_validate(turno).model_dump()
    return success_response(message="Asignación de técnico y dron completada", data=data)
