from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import NotificacionUseCases
from app.presentation.api.dependencies.auth import get_current_user, RoleChecker
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

admin_required = RoleChecker(["administrador"])

@router.get("")
def list_notificaciones(
    leido: int = Query(None, description="0 = no leídas, 1 = leídas. Omitir para todas."),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Retorna el listado de notificaciones para el usuario autenticado."""
    leido_bool = None
    if leido is not None:
        leido_bool = True if leido == 1 else False
        
    notifs = NotificacionUseCases.ver_notificaciones(db, current_user, leido_bool)
    data = [schemas.NotificacionResponse.model_validate(n).model_dump() for n in notifs]
    return success_response(message="Notificaciones obtenidas exitosamente", data=data)

@router.patch("/{id_notificacion}/leer")
def marcar_leida(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Marca la notificación indicada como leída (leido = 1)."""
    notif = NotificacionUseCases.marcar_leida(db, id_notificacion, current_user)
    data = schemas.NotificacionResponse.model_validate(notif).model_dump()
    return success_response(message="Notificación marcada como leída", data=data)

@router.post("", status_code=status.HTTP_201_CREATED)
def crear_notificacion(
    request: schemas.NotificacionCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Crea y envía una notificación a un usuario. Solo administrador o sistema."""
    notif = NotificacionUseCases.crear_notificacion(db, request)
    data = schemas.NotificacionResponse.model_validate(notif).model_dump()
    return success_response(message="Notificación enviada exitosamente", data=data, status_code=201)

@router.delete("/clear-all")
def borrar_todas_notificaciones(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Elimina todas las notificaciones del usuario autenticado (o todas si es administrador)."""
    from app.infrastructure.database.models.models import NotificacionModel
    if current_user.rol == "administrador":
        rows = db.query(NotificacionModel).delete()
    else:
        rows = db.query(NotificacionModel).filter(NotificacionModel.id_usuario == current_user.id_usuarios).delete()
    db.commit()
    return success_response(message=f"Se eliminaron {rows} notificaciones exitosamente")

@router.delete("/{id_notificacion}")
def borrar_notificacion(
    id_notificacion: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Elimina una notificación específica."""
    from app.infrastructure.database.models.models import NotificacionModel
    from app.shared.exceptions.exceptions import NotFoundException
    query = db.query(NotificacionModel).filter(NotificacionModel.id_notificacion == id_notificacion)
    if current_user.rol != "administrador":
        query = query.filter(NotificacionModel.id_usuario == current_user.id_usuarios)
    notif = query.first()
    if not notif:
        raise NotFoundException("Notificación no encontrada")
    db.delete(notif)
    db.commit()
    return success_response(message="Notificación eliminada exitosamente")
