from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import AdminUsuarioUseCases, AuthUseCases
from app.presentation.api.dependencies.auth import RoleChecker
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/admin/usuarios", tags=["Administración de Usuarios"])

# Restringir router exclusivamente a Administradores
admin_required = RoleChecker(["administrador"])

@router.get("")
def list_usuarios(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Lista todos los usuarios del sistema junto con sus perfiles de forma detallada. Solo administradores."""
    usuarios = AdminUsuarioUseCases.list_all_users(db)
    
    # Construir respuesta detallada con perfiles asociados
    data = []
    for u in usuarios:
        profile_data = None
        if u.rol == "cliente" and u.cliente:
            profile_data = {
                "id_cliente": u.cliente.id_cliente,
                "nombre": u.cliente.nombre,
                "apellido_1": u.cliente.apellido_1,
                "apellido_2": u.cliente.apellido_2,
                "telefono": u.cliente.telefono,
                "ciudad_expedicion": u.cliente.ciudad_expedicion,
                "fecha_expedicion": u.cliente.fecha_expedicion,
                "verificado": u.cliente.verificado
            }
        elif u.rol == "tecnico" and u.tecnico:
            profile_data = {
                "id_tecnico": u.tecnico.id_tecnico,
                "nombre": u.tecnico.nombre,
                "apellido_1": u.tecnico.apellido_1,
                "apellido_2": u.tecnico.apellido_2,
                "telefono": u.tecnico.telefono,
                "certificacion": u.tecnico.certificacion,
                "estado": u.tecnico.estado
            }
            
        data.append({
            "id_usuarios": u.id_usuarios,
            "email": u.email,
            "rol": u.rol,
            "fecha_de_creacion": u.fecha_de_creacion.isoformat() if u.fecha_de_creacion else None,
            "perfil": profile_data
        })
        
    return success_response(message="Listado de usuarios obtenido", data=data)

@router.post("", status_code=status.HTTP_201_CREATED)
def crear_usuario_por_admin(
    request: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Permite al administrador registrar directamente cualquier tipo de cuenta (Admin, Técnico o Cliente)."""
    user = AuthUseCases.register_user(db, request)
    data = {
        "id_usuarios": user.id_usuarios,
        "email": user.email,
        "rol": user.rol,
        "fecha_de_creacion": user.fecha_de_creacion.isoformat() if user.fecha_de_creacion else None
    }
    return success_response(message="Usuario creado exitosamente por el administrador", data=data, status_code=201)

@router.put("/{id_usuario}")
def actualizar_usuario_por_admin(
    id_usuario: int,
    payload: dict = None,
    email: str = Query(None, description="Nuevo correo electrónico"),
    rol: str = Query(None, description="Nuevo rol: cliente, tecnico, administrador"),
    contraseña: str = Query(None, description="Nueva contraseña (mínimo 6 caracteres)"),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Permite al administrador actualizar email, rol y/o contraseña de cualquier usuario."""
    if payload:
        email = payload.get("email", email)
        rol = payload.get("rol", rol)
        contraseña = payload.get("contraseña", payload.get("nueva_contrasena", contraseña))

    user = AdminUsuarioUseCases.update_user_by_admin(db, id_usuario, email, rol)
    
    if contraseña:
        AdminUsuarioUseCases.reset_password_by_admin(db, id_usuario, contraseña)
    
    data = {
        "id_usuarios": user.id_usuarios,
        "email": user.email,
        "rol": user.rol
    }
    return success_response(message="Usuario actualizado exitosamente", data=data)

@router.put("/{id_usuario}/rol")
def actualizar_rol_usuario(
    id_usuario: int,
    request: schemas.UsuarioUpdateRol,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    user = AdminUsuarioUseCases.update_user_by_admin(db, id_usuario, rol=request.rol)
    return success_response(message="Rol de usuario actualizado exitosamente", data={"id_usuarios": user.id_usuarios, "rol": user.rol})

@router.put("/{id_usuario}/password")
@router.post("/{id_usuario}/password")
def restablecer_password_usuario(
    id_usuario: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    nueva_pass = request.get("nueva_contrasena") or request.get("contraseña") or request.get("password") or request.get("nueva_contraseña")
    if not nueva_pass or len(str(nueva_pass).strip()) < 6:
        from app.shared.exceptions.exceptions import ValidationException
        raise ValidationException("La contraseña debe tener al menos 6 caracteres.")
    
    user = AdminUsuarioUseCases.reset_password_by_admin(db, id_usuario, str(nueva_pass).strip())
    return success_response(message="Contraseña restablecida exitosamente", data={"id_usuarios": user.id_usuarios})

@router.get("/config/sistema")
def get_system_config(
    db: Session = Depends(get_db)
):
    """Obtiene la configuración corporativa persistida en base de datos (público para sincronización de canales)."""
    from app.infrastructure.database.models.models import SystemConfigModel
    config_record = db.query(SystemConfigModel).filter(SystemConfigModel.clave == "perfil_corporativo").first()
    import json
    data = json.loads(config_record.valor) if config_record and config_record.valor else {
        "empresa": "Flymetrics Colombia S.A.S.",
        "nit": "900.123.456-7",
        "telefono": "+57 315 542 9714",
        "whatsapp": "+57 315 542 9714",
        "email": "comercial@flymetrix.com.co",
        "direccion": "Avenida El Dorado #68b-70, Bogotá D.C.",
        "wa_template_24h": "Hola {nombre}, te contactamos desde Flymetrics Colombia sobre tu solicitud de cotización para {servicio}.",
        "wa_template_agendar": "Hola Flymetrics Colombia, acabo de agendar una solicitud de servicio / demostración:\nRadicado: {radicado}\nProductor: {nombre} (CC/NIT: {cedula})\nFinca: {finca} en {municipio} ({departamento})\nCultivo: {cultivo} ({hectareas} Ha)\nServicio: {servicio}\nFecha programada: {fecha}\nUbicación / Maps: {ubicacion_maps}\nDeseo coordinar detalles técnicos de campo con el piloto.",
        "wa_template_general": "Hola Flymetrics, deseo solicitar asesoría e información técnica sobre sus servicios de drones agrícolas."
    }
    return success_response(message="Configuración del sistema obtenida", data=data)

@router.put("/config/sistema")
def save_system_config(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Guarda y persiste la configuración corporativa en la base de datos."""
    from app.infrastructure.database.models.models import SystemConfigModel
    import json
    config_record = db.query(SystemConfigModel).filter(SystemConfigModel.clave == "perfil_corporativo").first()
    if not config_record:
        config_record = SystemConfigModel(clave="perfil_corporativo", valor=json.dumps(payload))
        db.add(config_record)
    else:
        config_record.valor = json.dumps(payload)
    db.commit()
    return success_response(message="Configuración corporativa guardada exitosamente en la base de datos", data=payload)

@router.delete("/{id_usuario}")
def eliminar_usuario_por_admin(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Elimina una cuenta de usuario y sus perfiles de cliente/técnico asociados en cascada. Solo administradores."""
    AdminUsuarioUseCases.delete_user_by_admin(db, id_usuario)
    return success_response(message="Usuario y perfiles asociados eliminados exitosamente")
