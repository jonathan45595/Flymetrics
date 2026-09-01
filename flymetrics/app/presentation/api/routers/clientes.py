from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import ClienteUseCases
from app.presentation.api.dependencies.auth import get_current_user, RoleChecker
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/clientes", tags=["Clientes"])

admin_or_tech = RoleChecker(["administrador", "tecnico"])
admin_required = RoleChecker(["administrador"])

@router.get("")
def list_clientes(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(admin_or_tech)):
    """Lista todos los clientes. Solo administradores y técnicos."""
    clientes = db.query(ClienteModel).all()
    data = [schemas.ClienteResponse.model_validate(c).model_dump() for c in clientes]
    return success_response(message="Lista de clientes obtenida", data=data)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_cliente_admin(
    request: schemas.ClienteAdminCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Crear cliente desde el panel administrador con o sin correo."""
    from app.infrastructure.security.jwt_handler import hash_password
    from app.infrastructure.database.models.models import FincaModel
    import uuid

    clean_email = (request.email or "").strip().lower()
    clean_nombre = (request.nombre or "").strip().upper()
    clean_tel = (request.telefono or "").strip()

    id_usuario = None
    if clean_email:
        # Si se proporcionó email, verificar que no esté repetido
        existing_user = db.query(UsuarioModel).filter(UsuarioModel.email == clean_email).first()
        if existing_user:
            from app.shared.exceptions.exceptions import BadRequestException
            raise BadRequestException(f"El correo '{clean_email}' ya está registrado en el sistema")
        
        pwd = request.contraseña or "Flymetrics123!"
        new_user = UsuarioModel(
            email=clean_email,
            contraseña=hash_password(pwd),
            rol="cliente"
        )
        db.add(new_user)
        db.flush()
        id_usuario = new_user.id_usuarios

    # Crear el perfil de Cliente
    cliente = ClienteModel(
        id_usuario=id_usuario,
        nombre=clean_nombre,
        apellido_1="",
        apellido_2="",
        telefono=clean_tel or None,
        verificado=True
    )
    db.add(cliente)
    db.flush()

    # Si se especificó nombre de finca o ubicación, crear finca asociada
    if request.nombre_finca or request.ubicacion_municipio or request.departamento:
        finca = FincaModel(
            id_cliente=cliente.id_cliente,
            nombre_finca=request.nombre_finca or "Finca Principal",
            departamento=request.departamento or "Cundinamarca",
            ubicacion_municipio=request.ubicacion_municipio or "Municipio Principal",
            hectareas=request.hectareas or 10.0
        )
        db.add(finca)

    db.commit()
    db.refresh(cliente)

    data = schemas.ClienteResponse.model_validate(cliente).model_dump()
    return success_response(message="Cliente registrado exitosamente", data=data, status_code=201)

@router.get("/me")
def get_me(db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Retorna el perfil del cliente autenticado según su JWT. Crea el perfil si no existe aún."""
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
    if not cliente:
        name = current_user.email.split('@')[0]
        cliente = ClienteModel(
            id_usuario=current_user.id_usuarios,
            nombre=name,
            apellido_1='Cliente',
            telefono='',
            verificado=True
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    data = schemas.ClienteResponse.model_validate(cliente).model_dump()
    return success_response(message="Perfil obtenido exitosamente", data=data)

@router.get("/{id_cliente}")
def get_cliente_detail(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_or_tech)
):
    """Detalle completo de un cliente incluyendo sus fincas y correo de acceso."""
    from app.shared.exceptions.exceptions import NotFoundException
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == id_cliente).first()
    if not cliente:
        raise NotFoundException("Cliente no encontrado")
    
    fincas_data = []
    for f in cliente.fincas:
        fincas_data.append({
            "id_finca": f.id_finca,
            "nombre_finca": f.nombre_finca,
            "ubicacion_municipio": f.ubicacion_municipio,
            "departamento": f.departamento,
            "hectareas": float(f.hectareas or 0)
        })
        
    data = {
        "id_cliente": cliente.id_cliente,
        "id_usuario": cliente.id_usuario,
        "email": cliente.usuario.email if cliente.usuario else None,
        "nombre": cliente.nombre,
        "apellido_1": cliente.apellido_1,
        "apellido_2": cliente.apellido_2,
        "telefono": cliente.telefono,
        "numero_documento": cliente.numero_documento,
        "ciudad_expedicion": cliente.ciudad_expedicion,
        "fecha_expedicion": cliente.fecha_expedicion,
        "verificado": cliente.verificado,
        "link_alegra": cliente.link_alegra,
        "fincas": fincas_data
    }
    return success_response(message="Detalle de cliente obtenido", data=data)

@router.put("/{id_cliente}/alegra")
def set_cliente_alegra_link(
    id_cliente: int,
    request: schemas.ClienteAlegraRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """Vincula el enlace del portal/factura de Alegra para un cliente específico. Solo administrador."""
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == id_cliente).first()
    if not cliente:
        from app.shared.exceptions.exceptions import NotFoundException
        raise NotFoundException("Cliente no encontrado")
    cliente.link_alegra = (request.link_alegra or "").strip()
    db.commit()
    db.refresh(cliente)
    data = schemas.ClienteResponse.model_validate(cliente).model_dump()
    return success_response(message="Enlace de facturación Alegra vinculado exitosamente", data=data)

@router.put("/{id_cliente}/admin-verificar")
@router.patch("/{id_cliente}/verificar")
def admin_verificar_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """El administrador marca un cliente como verificado directamente. Solo administrador."""
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == id_cliente).first()
    if not cliente:
        from app.shared.exceptions.exceptions import NotFoundException
        raise NotFoundException("Cliente no encontrado")
    cliente.verificado = True
    db.commit()
    db.refresh(cliente)
    data = schemas.ClienteResponse.model_validate(cliente).model_dump()
    return success_response(message="Cliente verificado exitosamente", data=data)

@router.post("/completar-verificacion")
def completar_verificacion_cliente(
    request: schemas.CompletarVerificacionClienteRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """Guarda Cédula/NIT, Nombre Completo y Fecha de Nacimiento del cliente autenticado y marca verificado=True.
    Si el NIT ya pertenece a otra cuenta, solicita autenticación/contraseña de la cuenta anterior para transferirlo.
    """
    from app.infrastructure.security.jwt_handler import verify_password
    from app.shared.exceptions.exceptions import ConflictException, UnauthorizedException

    raw_n = (request.nombre or "").strip()
    raw_a1 = (request.apellido_1 or "").strip()
    full_name = " ".join([p for p in [raw_n, raw_a1] if p]).strip() or "Cliente"

    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
    if not cliente:
        cliente = ClienteModel(
            id_usuario=current_user.id_usuarios,
            nombre=full_name,
            apellido_1="",
            apellido_2="",
            numero_documento=request.numero_documento,
            fecha_nacimiento=request.fecha_nacimiento,
            verificado=False
        )
        db.add(cliente)
        db.flush()

    num_doc = (request.numero_documento or "").strip()
    if num_doc:
        # Buscar si el NIT / Documento pertenece a otro cliente
        other_cliente = db.query(ClienteModel).filter(
            ClienteModel.numero_documento == num_doc,
            ClienteModel.id_cliente != cliente.id_cliente
        ).first()

        if other_cliente:
            other_user = other_cliente.usuario
            nombre_titular = other_cliente.nombre or "Titular Anterior"
            email_titular = other_user.email if other_user else "cuenta_anterior@flymetrics.co"

            if not request.transfer_password:
                # Lanzar conflicto con los detalles de la cuenta anterior
                raise ConflictException(
                    f"El NIT / Documento '{num_doc}' ya se encuentra registrado y verificado en la cuenta de '{nombre_titular}' ({email_titular}). "
                    f"Para transferir el NIT a tu cuenta actual, por favor inicia sesión en la cuenta anterior para autorizar la transferencia.",
                    errors=[{
                        "nit": num_doc,
                        "nombre_titular": nombre_titular,
                        "email_titular": email_titular,
                        "requires_transfer_auth": True
                    }]
                )
            else:
                # Validar la contraseña del titular anterior
                if not other_user or not verify_password(request.transfer_password, other_user.contraseña):
                    raise UnauthorizedException(
                        "La contraseña ingresada para la cuenta anterior es incorrecta. No se pudo autorizar la transferencia del NIT."
                    )

                # Autorizado: desasociar NIT de la cuenta anterior
                other_cliente.numero_documento = None
                other_cliente.verificado = False
                db.add(other_cliente)
                db.flush()

    cliente.numero_documento = num_doc
    cliente.nombre = full_name
    cliente.apellido_1 = ""
    cliente.apellido_2 = ""
    cliente.fecha_nacimiento = request.fecha_nacimiento
    cliente.verificado = True
        
    db.commit()
    db.refresh(cliente)
    
    data = {
        "id_cliente": cliente.id_cliente,
        "id_usuario": cliente.id_usuario,
        "email": current_user.email,
        "nombre": cliente.nombre,
        "apellido_1": "",
        "apellido_2": "",
        "numero_documento": cliente.numero_documento,
        "fecha_nacimiento": cliente.fecha_nacimiento,
        "verificado": True
    }
    return success_response(message="✓ Verificación de datos personales completada con éxito.", data=data)




@router.put("/{id_cliente}")
def update_profile(id_cliente: int, request: schemas.ClienteUpdate, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Actualiza los datos del perfil de cliente."""
    cliente = ClienteUseCases.update_profile(db, id_cliente, request, current_user)
    data = schemas.ClienteResponse.model_validate(cliente).model_dump()
    return success_response(message="Perfil de cliente actualizado", data=data)

@router.post("/{id_cliente}/verificar-cc")
def verify_cc(id_cliente: int, request: schemas.ClienteVerifyRequest, db: Session = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    """Valida los datos de cédula (CC) con el bot de IA de Flymetrics y marca el cliente como verificado."""
    result = ClienteUseCases.verify_document_ia(db, id_cliente, request, current_user)
    return success_response(message="Verificación de documento completada", data=result)
