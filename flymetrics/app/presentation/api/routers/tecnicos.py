from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import TecnicoUseCases
from app.presentation.api.dependencies.auth import get_current_user, RoleChecker
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

# Solo el administrador puede crear perfiles de técnico y listar a todos
admin_required = RoleChecker(["administrador"])



@router.get("")
def list_all(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Retorna la lista de todos los técnicos del sistema. Protegido por JWT."""
    tecnicos = TecnicoUseCases.list_all(db)
    data = [schemas.TecnicoResponse.model_validate(t).model_dump() for t in tecnicos]
    return success_response(message="Lista de técnicos obtenida exitosamente", data=data)

class TecnicoRegisterRequest(schemas.UsuarioCreate):
    certificacion: str = None

@router.post("", status_code=status.HTTP_201_CREATED)
def create_tecnico(request: TecnicoRegisterRequest, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(admin_required)):
    """Crea un nuevo usuario con rol tecnico y su perfil."""
    from app.application.use_cases.use_cases import AuthUseCases
    user_req = schemas.UsuarioCreate(
        email=request.email,
        contraseña=request.contraseña,
        rol="tecnico",
        nombre=request.nombre,
        apellido_1=request.apellido_1,
        apellido_2=request.apellido_2,
        telefono=request.telefono
    )
    user = AuthUseCases.register_user(db, user_req)
    
    # Update certificacion in the profile created by AuthUseCases
    tecnico = TecnicoUseCases.get_by_id(db, user.tecnico.id_tecnico)
    update_req = schemas.TecnicoUpdate(certificacion=request.certificacion)
    TecnicoUseCases.update_profile(db, tecnico.id_tecnico, update_req)
    
    return success_response(message="Técnico creado exitosamente", data={"id": user.tecnico.id_tecnico}, status_code=201)

@router.get("/{id_tecnico}")
def get_by_id(id_tecnico: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Detalle de un técnico específico. Protegido por JWT."""
    tecnico = TecnicoUseCases.get_by_id(db, id_tecnico)
    data = schemas.TecnicoResponse.model_validate(tecnico).model_dump()
    return success_response(message="Detalle de técnico obtenido", data=data)

@router.put("/{id_tecnico}")
def update_profile(id_tecnico: int, request: schemas.TecnicoUpdate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(admin_required)):
    """Actualiza datos del perfil del técnico (estado, certificación, etc.). Solo administrador."""
    tecnico = TecnicoUseCases.update_profile(db, id_tecnico, request)
    data = schemas.TecnicoResponse.model_validate(tecnico).model_dump()
    return success_response(message="Perfil de técnico actualizado", data=data)

@router.get("/{id_tecnico}/calendario-ocupacion")
def get_calendario_ocupacion(
    id_tecnico: int,
    anio: int = Query(...),
    mes: int = Query(...),
    id_finca: int = Query(None),
    id_servicio: int = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Consulta la mapa de ocupación del técnico por mes."""
    from app.infrastructure.database.models.models import AgendaModel
    import calendar
    from datetime import date

    _, num_days = calendar.monthrange(anio, mes)
    start_date = date(anio, mes, 1)
    end_date = date(anio, mes, num_days)

    turnos = db.query(AgendaModel).filter(
        AgendaModel.id_tecnico == id_tecnico,
        AgendaModel.fecha_de_turno >= start_date,
        AgendaModel.fecha_de_turno <= end_date,
        AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"])
    ).all()

    ocupados_por_fecha = {}
    for t in turnos:
        d_str = str(t.fecha_de_turno)
        ocupados_por_fecha[d_str] = ocupados_por_fecha.get(d_str, 0) + 1

    result = {}
    for day in range(1, num_days + 1):
        d_str = f"{anio}-{mes:02d}-{day:02d}"
        count = ocupados_por_fecha.get(d_str, 0)
        estado = "libre" if count == 0 else ("parcial" if count < 3 else "ocupado")
        result[d_str] = estado

    return success_response(message="Calendario de ocupación obtenido", data=result)


@router.get("/{id_tecnico}/disponibilidad")
def get_disponibilidad_tecnico(
    id_tecnico: int,
    fecha: date = Query(...),
    id_finca: int = Query(...),
    id_servicio: int = Query(...),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Consulta los slots de tiempo disponibles para un técnico en una fecha específica."""
    from app.infrastructure.database.models.models import FincaModel, AgendaModel
    finca = db.query(FincaModel).filter(FincaModel.id_finca == id_finca).first()
    hectareas = float(finca.hectareas or 1.0) if finca else 1.0
    duracion_horas = max(1.0, round(hectareas / 5.0, 1))

    turnos = db.query(AgendaModel).filter(
        AgendaModel.id_tecnico == id_tecnico,
        AgendaModel.fecha_de_turno == fecha,
        AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"])
    ).all()

    busy_intervals = []
    for t in turnos:
        if t.hora_inicio_estimada and t.hora_fin_estimada:
            h_start = t.hora_inicio_estimada.hour * 60 + t.hora_inicio_estimada.minute
            h_end = t.hora_fin_estimada.hour * 60 + t.hora_fin_estimada.minute
            busy_intervals.append((h_start, h_end))

    start_min = 360  # 06:00 AM
    end_min = 1080   # 06:00 PM
    dur_min = int(duracion_horas * 60)

    slots_disponibles = []
    for current in range(start_min, end_min - dur_min + 1, 30):
        slot_end = current + dur_min
        overlap = False
        for b_start, b_end in busy_intervals:
            if current < b_end and slot_end > b_start:
                overlap = True
                break
        if not overlap:
            h = current // 60
            m = current % 60
            slots_disponibles.append(f"{h:02d}:{m:02d}:00")

    data = {
        "duracion_horas": duracion_horas,
        "slots_disponibles": slots_disponibles
    }
    return success_response(message="Disponibilidad obtenida exitosamente", data=data)


@router.delete("/{id_tecnico}")
def delete_tecnico(id_tecnico: int, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(admin_required)):
    """Elimina un técnico. Solo administrador."""
    TecnicoUseCases.delete_tecnico(db, id_tecnico)
    return success_response(message="Técnico eliminado exitosamente")


