from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import AuthUseCases
from app.presentation.api.dependencies.auth import get_current_user
from app.infrastructure.database.models.models import UsuarioModel
from app.shared.responses.response import success_response
from app.shared.exceptions.exceptions import BadRequestException

router = APIRouter(prefix="/auth", tags=["Autenticación"])

async def get_login_credentials(request: Request) -> tuple:
    """Extrae las credenciales del cuerpo de la petición (JSON o Formulario).
    Retorna una tupla (UsuarioLogin, es_formulario).
    """
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        email = form_data.get("username")
        contraseña = form_data.get("password")
        if not email or not contraseña:
            raise BadRequestException("Credenciales incompletas en formulario de login")
        return schemas.UsuarioLogin(email=email, contraseña=contraseña), True
    else:
        try:
            body = await request.json()
            return schemas.UsuarioLogin(**body), False
        except Exception:
            raise BadRequestException("Cuerpo de solicitud de login inválido (se esperaba JSON o Form)")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo registro en tabla_usuarios. La contraseña se hashea con Bcrypt."""
    user = AuthUseCases.register_user(db, request)
    data = {
        "id_usuarios": user.id_usuarios,
        "email": user.email,
        "rol": user.rol,
        "fecha_de_creacion": user.fecha_de_creacion.isoformat() if user.fecha_de_creacion else None
    }
    return success_response(message="Usuario registrado exitosamente", data=data, status_code=201)

@router.post("/login")
def login(
    credentials_data: tuple = Depends(get_login_credentials),
    db: Session = Depends(get_db)
):
    """Valida credenciales y retorna un JWT firmado (HS256) con expiración de 8h."""
    credentials, es_formulario = credentials_data
    auth_data = AuthUseCases.login_user(db, credentials)
    
    if es_formulario:
        # Formato estándar de OAuth2 para Swagger UI
        return {
            "access_token": auth_data["token"],
            "token_type": "bearer"
        }
    
    return success_response(message="Inicio de sesión exitoso", data=auth_data)

@router.post("/google")
def google_login(request: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    """Simula el inicio de sesión con Google OAuth. Retorna un token JWT."""
    auth_data = AuthUseCases.login_google(db, request)
    return success_response(message="Autenticación con Google exitosa", data=auth_data)

@router.get("/me")
def get_me(current_user: UsuarioModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna datos del usuario activo según el JWT recibido enriquecido con perfil."""
    data = {
        "id_usuarios": current_user.id_usuarios,
        "email": current_user.email,
        "rol": current_user.rol,
        "fecha_de_creacion": current_user.fecha_de_creacion.isoformat() if current_user.fecha_de_creacion else None
    }
    
    if current_user.rol == "tecnico":
        from app.infrastructure.database.models.models import TecnicoModel
        tec = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
        if not tec:
            tec = db.query(TecnicoModel).filter(TecnicoModel.email == current_user.email).first()
        if tec:
            data["id_tecnico"] = tec.id_tecnico
            data["nombre"] = tec.nombre
            data["apellido_1"] = tec.apellido_1 or ""
            data["telefono"] = tec.telefono or ""
            data["certificacion"] = tec.certificacion or "RPAS-A-102030"
            data["estado"] = tec.estado or "disponible"
        else:
            default_nom = current_user.email.split('@')[0].capitalize()
            data["nombre"] = default_nom
            data["apellido_1"] = "Piloto"
            data["telefono"] = ""
            data["certificacion"] = "RPAS-A-102030"
            data["estado"] = "disponible"
    elif current_user.rol == "cliente":
        if current_user.cliente:
            c = current_user.cliente
            data["id_cliente"] = c.id_cliente
            data["nombre"] = c.nombre
            data["apellido_1"] = c.apellido_1 or ""
            data["telefono"] = c.telefono or ""
            data["link_alegra"] = getattr(c, 'link_alegra', None)
        else:
            data["nombre"] = current_user.email.split('@')[0].capitalize()
            data["apellido_1"] = "Cliente"
    elif current_user.rol == "administrador":
        data["nombre"] = "Administrador"
        data["apellido_1"] = "Flymetrics"

    return success_response(message="Usuario obtenido exitosamente", data=data)

import random

@router.post("/enviar-codigo-verificacion")
def enviar_codigo_verificacion(
    request: schemas.SolicitudCodigoRequest,
    db: Session = Depends(get_db)
):
    """Genera y guarda un código OTP numérico de 6 dígitos para el correo del usuario."""
    from app.infrastructure.database.models.models import ClienteModel
    user = db.query(UsuarioModel).filter(UsuarioModel.email == request.email).first()
    if not user:
        raise BadRequestException("El correo especificado no se encuentra registrado en el sistema.")
    
    # Generar OTP de 6 dígitos
    codigo = f"{random.randint(100000, 999999)}"
    
    if user.cliente:
        user.cliente.codigo_verificacion = codigo
    else:
        cliente = ClienteModel(
            id_usuario=user.id_usuarios,
            nombre=user.email.split('@')[0],
            apellido_1="Cliente",
            codigo_verificacion=codigo,
            verificado=False
        )
        db.add(cliente)
    
    db.commit()
    
    # Enviar correo real / SMTP con la plantilla de verificación
    from app.shared.utils.email_service import send_otp_email
    send_otp_email(request.email, codigo)
    
    return success_response(
        message=f"Código de verificación enviado exitosamente a {request.email}",
        data={"codigo_simulado": codigo, "email": request.email}
    )

@router.post("/verificar-codigo-correo")
def verificar_codigo_correo(
    request: schemas.VerificacionCodigoRequest,
    db: Session = Depends(get_db)
):
    """Valida el código OTP de 6 dígitos ingresado por el usuario."""
    user = db.query(UsuarioModel).filter(UsuarioModel.email == request.email).first()
    if not user or not user.cliente:
        raise BadRequestException("No se encontró el registro de la cuenta.")
    
    if not user.cliente.codigo_verificacion or user.cliente.codigo_verificacion != request.codigo.strip():
        raise BadRequestException("El código ingresado es incorrecto o ha expirado.")
    
    return success_response(
        message="Correo electrónico confirmado. Procede a registrar tu Cédula, Nombre Completo y Fecha de Nacimiento.",
        data={"verificado_correo": True, "email": request.email}
    )

@router.post("/change-password")
@router.post("/cambiar-contrasena")
def change_password(
    request: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Permite a cualquier usuario autenticado cambiar su contraseña en la base de datos."""
    from app.infrastructure.security.jwt_handler import hash_password, verify_password
    current_pwd = request.get("current_password") or request.get("contrasena_actual") or request.get("current_pwd")
    new_pwd = request.get("new_password") or request.get("nueva_contrasena") or request.get("contraseña") or request.get("password")
    
    if not new_pwd or len(str(new_pwd).strip()) < 6:
        raise BadRequestException("La nueva contraseña debe tener al menos 6 caracteres")
        
    if current_pwd and not verify_password(current_pwd, current_user.contraseña):
        raise BadRequestException("La contraseña actual es incorrecta")
        
    current_user.contraseña = hash_password(str(new_pwd).strip())
    db.commit()
    db.refresh(current_user)
    return success_response(message="Contraseña actualizada exitosamente en la base de datos")

