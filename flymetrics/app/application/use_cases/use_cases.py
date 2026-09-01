from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, time, timedelta, date
from decimal import Decimal
import random

from app.infrastructure.database.models.models import (
    UsuarioModel, ClienteModel, TecnicoModel, FincaModel,
    ServicioModel, AgendaModel, ReporteVueloModel, DroneModel,
    MantenimientoModel, EntregableModel, PagoModel, NotificacionModel,
    PQRModel, MensajePQRModel
)
from app.application.dto import schemas
from app.infrastructure.security.jwt_handler import hash_password, verify_password, create_access_token
from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.external.ai_verifier import AIVerifierService
from app.infrastructure.external.whatsapp_service import WhatsAppService
from app.infrastructure.external.google_auth import GoogleAuthService
from app.shared.exceptions.exceptions import (
    NotFoundException, BadRequestException, ConflictException, UnauthorizedException, ForbiddenException
)

# ==========================================
# 1. CASOS DE USO DE AUTENTICACIÓN
# ==========================================
class AuthUseCases:
    @staticmethod
    def register_user(db: Session, request: schemas.UsuarioCreate) -> UsuarioModel:
        # Validar si el email ya existe de forma insensible a mayúsculas
        clean_email = (request.email or "").strip().lower()
        if not clean_email:
            raise BadRequestException("El correo electrónico es obligatorio")

        existing = db.query(UsuarioModel).filter(func.lower(UsuarioModel.email) == clean_email).first()
        if existing:
            raise BadRequestException(f"El correo electrónico '{request.email}' ya se encuentra registrado en el sistema. Por favor utiliza otro correo o inicia sesión.")
            
        if request.telefono:
            clean_tel = str(request.telefono).strip()
            if clean_tel:
                exist_tel_cli = db.query(ClienteModel).filter(ClienteModel.telefono == clean_tel).first()
                exist_tel_tec = db.query(TecnicoModel).filter(TecnicoModel.telefono == clean_tel).first()
                if exist_tel_cli or exist_tel_tec:
                    raise BadRequestException(f"El número telefónico '{clean_tel}' ya está registrado en el sistema por otro usuario.")
            
        if request.rol not in ["cliente", "tecnico", "administrador"]:
            raise BadRequestException("Rol inválido. Debe ser 'cliente', 'tecnico' o 'administrador'")
            
        hashed = hash_password(request.contraseña)
        user = UsuarioModel(
            email=request.email,
            contraseña=hashed,
            rol=request.rol
        )
        db.add(user)
        db.flush()  # Generar id_usuarios

        # Save full name directly into nombre
        raw_nombre = (request.nombre or "").strip()
        raw_ap1 = (request.apellido_1 or "").strip()
        raw_ap2 = (request.apellido_2 or "").strip()

        # Combine into a single full name if separated, or take full name as provided
        full_name_parts = [raw_nombre, raw_ap1, raw_ap2]
        full_name = " ".join([p for p in full_name_parts if p]).strip() or "Usuario"

        telefono = request.telefono

        if request.rol == "cliente":
            cliente = ClienteModel(
                id_usuario=user.id_usuarios,
                nombre=full_name,
                apellido_1="",
                apellido_2="",
                telefono=telefono,
                verificado=True
            )
            db.add(cliente)
        elif request.rol == "tecnico":
            tecnico = TecnicoModel(
                id_usuario=user.id_usuarios,
                nombre=full_name,
                apellido_1="",
                apellido_2="",
                certificacion="RAC-100-PENDIENTE",
                telefono=telefono,
                estado="disponible"
            )
            db.add(tecnico)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login_user(db: Session, request: schemas.UsuarioLogin) -> dict:
        clean_email = (request.email or "").strip().lower()
        if not clean_email:
            raise BadRequestException("El correo electrónico es obligatorio")

        user = db.query(UsuarioModel).filter(func.lower(UsuarioModel.email) == clean_email).first()
        if not user or not verify_password(request.contraseña, user.contraseña):
            raise UnauthorizedException("Credenciales incorrectas")
            
        # Generar token JWT
        token_data = {"sub": user.email, "rol": user.rol, "id_usuarios": user.id_usuarios}
        token = create_access_token(token_data)
        
        return {
            "token": token,
            "rol": user.rol,
            "id_usuarios": user.id_usuarios,
            "email": user.email
        }

    @staticmethod
    def login_google(db: Session, request: schemas.GoogleLoginRequest) -> dict:
        # Verificar token de Google
        google_data = GoogleAuthService.verify_google_token(request.token)
        email = google_data["email"]
        
        # Buscar usuario en la base de datos
        user = db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        if not user:
            # Registrar nuevo usuario cliente
            random_pwd = hash_password(f"GoogleSecret_{random.randint(100000, 999999)}")
            user = UsuarioModel(
                email=email,
                contraseña=random_pwd,
                rol="cliente"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Nombre completo desde Google
            g_full_name = f"{google_data.get('nombre', '')} {google_data.get('apellido_1', '')}".strip() or email.split('@')[0]

            # Crear perfil de cliente asociado con nombre completo
            cliente = ClienteModel(
                id_usuario=user.id_usuarios,
                nombre=g_full_name,
                apellido_1="",
                apellido_2="",
                telefono="",
                verificado=False
            )
            db.add(cliente)
            db.commit()
            
        token_data = {"sub": user.email, "rol": user.rol, "id_usuarios": user.id_usuarios}
        token = create_access_token(token_data)
        
        return {
            "token": token,
            "rol": user.rol,
            "id_usuarios": user.id_usuarios,
            "email": user.email
        }

class AdminUsuarioUseCases:
    @staticmethod
    def list_all_users(db: Session) -> list:
        """Lista todos los usuarios del sistema para el administrador."""
        return db.query(UsuarioModel).all()

    @staticmethod
    def update_user_by_admin(db: Session, user_id: int, email: str = None, rol: str = None) -> UsuarioModel:
        """Permite al administrador modificar los datos generales de una cuenta de usuario."""
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == user_id).first()
        if not user:
            raise NotFoundException("Usuario no encontrado")
            
        if email:
            existing = db.query(UsuarioModel).filter(UsuarioModel.email == email, UsuarioModel.id_usuarios != user_id).first()
            if existing:
                raise BadRequestException("El correo electrónico ya está registrado por otro usuario")
            user.email = email
            
        if rol:
            if rol not in ["cliente", "tecnico", "administrador"]:
                raise BadRequestException("Rol inválido. Debe ser 'cliente', 'tecnico' o 'administrador'")
            user.rol = rol
            
            # Sync profiles if changing role
            if rol == "cliente" and not user.cliente:
                cliente = ClienteModel(id_usuario=user.id_usuarios, nombre="Cliente", apellido_1="Registrado", verificado=True)
                db.add(cliente)
            elif rol == "tecnico" and not user.tecnico:
                tecnico = TecnicoModel(id_usuario=user.id_usuarios, nombre="Técnico", apellido_1="Registrado", certificacion="RAC-100", estado="disponible")
                db.add(tecnico)
            
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def reset_password_by_admin(db: Session, user_id: int, nueva_contrasena: str) -> UsuarioModel:
        """Permite al administrador restablecer la contraseña de un usuario."""
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == user_id).first()
        if not user:
            raise NotFoundException("Usuario no encontrado")
        if len(nueva_contrasena) < 6:
            raise BadRequestException("La contraseña debe tener al menos 6 caracteres")
        user.contraseña = hash_password(nueva_contrasena)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user_by_admin(db: Session, user_id: int) -> bool:
        """Elimina de forma segura un usuario y sus perfiles asociados en cascada."""
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == user_id).first()
        if not user:
            raise NotFoundException("Usuario no encontrado")
            
        db.delete(user)
        db.commit()
        return True


# ==========================================
# 2. CASOS DE USO DE CLIENTES
# ==========================================
class ClienteUseCases:
    @staticmethod
    def create_profile(db: Session, request: schemas.ClienteCreate, current_user_id: int) -> ClienteModel:
        # Verificar que el id_usuario existe
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == request.id_usuario).first()
        if not user:
            raise NotFoundException("El usuario especificado no existe")
            
        # Verificar que el usuario no tiene ya un perfil de cliente
        existing = db.query(ClienteModel).filter(ClienteModel.id_usuario == request.id_usuario).first()
        if existing:
            return existing
            
        # Full name resolution
        raw_n = (request.nombre or "").strip()
        raw_a1 = (request.apellido_1 or "").strip()
        raw_a2 = (request.apellido_2 or "").strip()
        full_name = " ".join([p for p in [raw_n, raw_a1, raw_a2] if p]).strip() or "Cliente"

        cliente = ClienteModel(
            id_usuario=request.id_usuario,
            nombre=full_name,
            apellido_1="",
            apellido_2="",
            telefono=request.telefono,
            verificado=False
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

    @staticmethod
    def get_me(db: Session, user_id: int) -> ClienteModel:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == user_id).first()
        if not cliente:
            raise NotFoundException("El usuario no tiene un perfil de cliente creado aún")
        return cliente

    @staticmethod
    def update_profile(db: Session, cliente_id: int, request: schemas.ClienteUpdate, current_user: UsuarioModel) -> ClienteModel:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == cliente_id).first()
        if not cliente:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente:
                raise NotFoundException("Perfil de cliente no encontrado")
            
        # Regla de negocio: El cliente solo puede editar su propio perfil
        if current_user.rol != "administrador" and cliente.id_usuario and cliente.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("No tienes permisos para editar este perfil de cliente")
            
        data = request.model_dump(exclude_unset=True)
        ced = data.pop("cedula", None)
        transfer_pwd = data.pop("transfer_password", None)
        if ced:
            data["numero_documento"] = ced

        # Handle full name
        n_val = data.get("nombre")
        a1_val = data.get("apellido_1")
        a2_val = data.get("apellido_2")
        if n_val is not None or a1_val is not None:
            full_n = " ".join([p for p in [n_val, a1_val, a2_val] if p]).strip()
            if full_n:
                data["nombre"] = full_n
                data["apellido_1"] = ""
                data["apellido_2"] = ""

        num_doc = (data.get("numero_documento") or "").strip()
        if num_doc:
            # Buscar si el NIT / Documento pertenece a otro cliente
            other_cliente = db.query(ClienteModel).filter(
                ClienteModel.numero_documento == num_doc,
                ClienteModel.id_cliente != cliente.id_cliente
            ).first()

            if other_cliente:
                # El NIT ya pertenece a otra cuenta
                other_user = other_cliente.usuario
                nombre_titular = f"{other_cliente.nombre or ''} {other_cliente.apellido_1 or ''}".strip() or "Titular Anterior"
                email_titular = other_user.email if other_user else "cuenta_anterior@flymetrics.co"

                if not transfer_pwd:
                    # Notificar al cliente que debe ingresar la contraseña de la cuenta propietaria para autorizar la transferencia
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
                    # Validar contraseña del usuario anterior
                    if not other_user or not verify_password(transfer_pwd, other_user.contraseña):
                        raise UnauthorizedException("La contraseña ingresada para la cuenta anterior es incorrecta. No se pudo autorizar la transferencia del NIT.")

                    # Autorizado: transferir NIT al nuevo cliente y dejar el usuario anterior en blanco
                    other_cliente.numero_documento = None
                    other_cliente.verificado = False
                    db.add(other_cliente)
                    db.flush()


            cliente.numero_documento = num_doc
            cliente.verificado = True

        if data.get("verificado") is not None:
            cliente.verificado = data.get("verificado")
            
        for key, value in data.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
            
        db.commit()
        db.refresh(cliente)
        return cliente

    @staticmethod
    def verify_document_ia(db: Session, cliente_id: int, request: schemas.ClienteVerifyRequest, current_user: UsuarioModel) -> dict:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == cliente_id).first()
        if not cliente:
            raise NotFoundException("Perfil de cliente no encontrado")
            
        if current_user.rol != "administrador" and cliente.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("No puedes verificar un documento de otro cliente")
            
        # Llamar al bot de IA simulado para validación del documento
        ia_result = AIVerifierService.verify_document(
            numero_documento=request.numero_documento,
            ciudad_expedicion=request.ciudad_expedicion,
            fecha_expedicion=request.fecha_expedicion
        )
        
        if not ia_result["success"]:
            raise BadRequestException(f"Error de verificación: {ia_result['mensaje']}")
            
        # Guardar en base de datos si la IA aprueba
        cliente.numero_documento = request.numero_documento
        cliente.ciudad_expedicion = request.ciudad_expedicion
        cliente.fecha_expedicion = request.fecha_expedicion
        cliente.verificado = True
        db.commit()
        
        # Enviar notificación de bienvenida / verificación
        notificacion = NotificacionModel(
            id_usuario=cliente.id_usuario,
            titulo="Cédula Verificada por IA",
            mensaje=f"Felicidades {cliente.nombre}, tu documento ha sido verificado con éxito por nuestro bot inteligente. Ya puedes programar turnos.",
            leido=False
        )
        db.add(notificacion)
        db.commit()
        
        return {
            "verificado": True,
            "mensaje": ia_result["mensaje"],
            "detalles": ia_result["detalles"]
        }


# ==========================================
# 3. CASOS DE USO DE TÉCNICOS
# ==========================================
class TecnicoUseCases:
    @staticmethod
    def create_profile(db: Session, request: schemas.TecnicoCreate) -> TecnicoModel:
        # Verificar que el usuario existe y es técnico
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == request.id_usuario).first()
        if not user:
            raise NotFoundException("El usuario especificado no existe")
            
        if user.rol != "tecnico":
            raise BadRequestException("El usuario asociado debe tener el rol de 'tecnico'")
            
        # Verificar que no tenga perfil técnico ya
        existing = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == request.id_usuario).first()
        if existing:
            return existing
            
        raw_n = (request.nombre or "").strip()
        raw_a1 = (request.apellido_1 or "").strip()
        raw_a2 = (request.apellido_2 or "").strip()
        full_name = " ".join([p for p in [raw_n, raw_a1, raw_a2] if p]).strip() or "Técnico"

        tecnico = TecnicoModel(
            id_usuario=request.id_usuario,
            nombre=full_name,
            apellido_1="",
            apellido_2="",
            certificacion=request.certificacion,
            telefono=request.telefono,
            estado="disponible",
            servicios_capacitados="1,2,3"
        )
        db.add(tecnico)
        db.commit()
        db.refresh(tecnico)
        return tecnico

    @staticmethod
    def list_all(db: Session) -> list:
        return db.query(TecnicoModel).all()

    @staticmethod
    def get_by_id(db: Session, tecnico_id: int) -> TecnicoModel:
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_tecnico == tecnico_id).first()
        if not tecnico:
            raise NotFoundException("Técnico no encontrado")
        return tecnico

    @staticmethod
    def update_profile(db: Session, tecnico_id: int, request: schemas.TecnicoUpdate) -> TecnicoModel:
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_tecnico == tecnico_id).first()
        if not tecnico:
            raise NotFoundException("Técnico no encontrado")
            
        data = request.model_dump(exclude_unset=True)
        n_val = data.get("nombre")
        a1_val = data.get("apellido_1")
        a2_val = data.get("apellido_2")
        if n_val is not None or a1_val is not None:
            full_n = " ".join([p for p in [n_val, a1_val, a2_val] if p]).strip()
            if full_n:
                data["nombre"] = full_n
                data["apellido_1"] = ""
                data["apellido_2"] = ""

        for key, value in data.items():
            setattr(tecnico, key, value)
            
        db.commit()
        db.refresh(tecnico)
        return tecnico

    @staticmethod
    def delete_tecnico(db: Session, tecnico_id: int) -> bool:
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_tecnico == tecnico_id).first()
        if not tecnico:
            raise NotFoundException("Técnico no encontrado")
        db.delete(tecnico)
        db.commit()
        return True


# ==========================================
# 4. CASOS DE USO DE FINCAS
# ==========================================
class FincaUseCases:
    @staticmethod
    def register_finca(db: Session, request: schemas.FincaCreate, current_user: UsuarioModel) -> FincaModel:
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente:
                cliente = ClienteModel(id_usuario=current_user.id_usuarios, nombre=current_user.email.split('@')[0], apellido_1="Cliente", verificado=True)
                db.add(cliente)
                db.commit()
                db.refresh(cliente)
            target_client_id = cliente.id_cliente
        else:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == request.id_cliente).first()
            target_client_id = cliente.id_cliente if cliente else request.id_cliente

        finca = FincaModel(
            id_cliente=target_client_id,
            nombre_finca=request.nombre_finca,
            ubicacion_municipio=request.ubicacion_municipio or "Yopal",
            departamento=request.departamento or "Casanare",
            hectareas=request.hectareas,
            latitud=request.latitud,
            longitud=request.longitud
        )
        db.add(finca)
        db.commit()
        db.refresh(finca)
        return finca


    @staticmethod
    def list_by_client(db: Session, current_user: UsuarioModel) -> list:
        if current_user.rol == "administrador":
            return db.query(FincaModel).all()
        cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
        if not cliente:
            cliente = ClienteModel(id_usuario=current_user.id_usuarios, nombre=current_user.email.split('@')[0], apellido_1="Cliente", verificado=True)
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
        return db.query(FincaModel).filter(FincaModel.id_cliente == cliente.id_cliente).all()

    @staticmethod
    def get_by_id(db: Session, finca_id: int, current_user: UsuarioModel) -> FincaModel:
        finca = db.query(FincaModel).filter(FincaModel.id_finca == finca_id).first()
        if not finca:
            raise NotFoundException("Finca no encontrada")
            
        # Si es cliente, verificar que le pertenece
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente or finca.id_cliente != cliente.id_cliente:
                raise ForbiddenException("La finca no pertenece al cliente autenticado")
                
        return finca

    @staticmethod
    def update_finca(db: Session, finca_id: int, request: schemas.FincaUpdate, current_user: UsuarioModel) -> FincaModel:
        finca = db.query(FincaModel).filter(FincaModel.id_finca == finca_id).first()
        if not finca:
            raise NotFoundException("Finca no encontrada")
            
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente or finca.id_cliente != cliente.id_cliente:
                raise ForbiddenException("No tienes permiso para actualizar esta finca")
                
        data = request.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(finca, key, value)
            
        db.commit()
        db.refresh(finca)
        return finca

    @staticmethod
    def delete_finca(db: Session, finca_id: int, current_user: UsuarioModel) -> bool:
        finca = db.query(FincaModel).filter(FincaModel.id_finca == finca_id).first()
        if not finca:
            raise NotFoundException("Finca no encontrada")
            
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente or finca.id_cliente != cliente.id_cliente:
                raise ForbiddenException("No tienes permiso para eliminar esta finca")
                
        # Verificar que no tenga turnos activos (Pendiente, Confirmado, En Proceso)
        active_turnos = db.query(AgendaModel).filter(
            AgendaModel.id_finca == finca_id,
            AgendaModel.estado.in_(["Pendiente", "Confirmado", "En Proceso"])
        ).first()
        
        if active_turnos:
            raise ConflictException("La finca tiene turnos activos, no se puede eliminar")
            
        db.delete(finca)
        db.commit()
        return True


# ==========================================
# 5. CASOS DE USO DE SERVICIOS
# ==========================================
class ServicioUseCases:
    @staticmethod
    def list_all(db: Session, only_active: bool = True) -> list:
        query = db.query(ServicioModel)
        if only_active:
            query = query.filter(ServicioModel.activo == True)
        return query.all()

    @staticmethod
    def create_servicio(db: Session, request: schemas.ServicioCreate) -> ServicioModel:
        servicio = ServicioModel(
            nombre_servicio=request.nombre_servicio,
            descripcion=request.descripcion,
            precio_base_m2=request.precio_base_m2
        )
        db.add(servicio)
        db.commit()
        db.refresh(servicio)
        return servicio

    @staticmethod
    def calculate_cotizacion(db: Session, request: schemas.CotizacionRequest) -> dict:
        servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == request.id_servicio).first()
        finca = db.query(FincaModel).filter(FincaModel.id_finca == request.id_finca).first()
        
        if not servicio:
            raise NotFoundException("El servicio especificado no existe")
        if not finca:
            raise NotFoundException("La finca especificada no existe")
            
        # Calcular precio base = precio por m2 * area en m2 (hectarea = 10,000 m2)
        hectareas = finca.hectareas or Decimal("1.00")
        area_m2 = hectareas * Decimal("10000.00")
        precio_base = round(servicio.precio_base_m2 * area_m2, 2)
        
        # Calcular logística vía GPS mock
        lat = float(finca.latitud) if finca.latitud is not None else 4.5709
        lng = float(finca.longitud) if finca.longitud is not None else -74.2973
        gps_data = GoogleMapsService.get_quote_data(lat, lng)
        costo_logistico = Decimal(str(gps_data["costo_logistico"]))
        
        precio_total = precio_base + costo_logistico
        
        return {
            "id_servicio": servicio.id_servicio,
            "id_finca": finca.id_finca,
            "nombre_servicio": servicio.nombre_servicio,
            "nombre_finca": finca.nombre_finca,
            "hectareas": hectareas,
            "precio_base": precio_base,
            "costo_logistico": costo_logistico,
            "precio_total": precio_total,
            "distancia_km": gps_data["distancia_km"],
            "duracion_estimada_horas": gps_data["duracion_estimada_horas"]
        }


# ==========================================
# 6. CASOS DE USO DE AGENDAMIENTO / CALENDARIO
# ==========================================
class AgendaUseCases:
    @staticmethod
    def crear_reserva_rapida(db: Session, request: schemas.ReservaRapidaCreate) -> dict:
        """Crea una reserva rápida para finqueros/productores sin exigir registro previo de contraseña."""
        from app.infrastructure.database.models.models import UsuarioModel, ClienteModel, FincaModel, ServicioModel, AgendaModel
        from app.infrastructure.security.jwt_handler import hash_password
        from app.shared.exceptions.exceptions import BadRequestException
        from decimal import Decimal
        from datetime import time, timedelta
        import re

        clean_cedula = re.sub(r'\D', '', request.cedula) or request.cedula.strip()
        clean_tel = re.sub(r'\D', '', request.telefono) or request.telefono.strip()
        email_user = request.email.strip().lower() if request.email else f"finquero_{clean_cedula or clean_tel}@flymetrics.co"

        # Validar fecha futura
        if request.fecha_deseada < date.today():
            raise BadRequestException("La fecha deseada del vuelo no puede ser en el pasado")

        # 1. Buscar UsuarioModel y ClienteModel
        user = None
        cliente = None

        if request.email and request.email.strip():
            user = db.query(UsuarioModel).filter(UsuarioModel.email == email_user).first()
            if user:
                cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == user.id_usuarios).first()

        if not cliente and clean_cedula:
            cliente = db.query(ClienteModel).filter(ClienteModel.numero_documento == clean_cedula).first()
            if cliente and cliente.id_usuario and not user:
                user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == cliente.id_usuario).first()

        if not cliente and clean_tel:
            cliente = db.query(ClienteModel).filter(ClienteModel.telefono == clean_tel).first()
            if cliente and cliente.id_usuario and not user:
                user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == cliente.id_usuario).first()

        if not user:
            user = db.query(UsuarioModel).filter(UsuarioModel.email == email_user).first()

        if not user:
            default_pass = clean_cedula if len(clean_cedula) >= 4 else clean_tel
            user = UsuarioModel(
                email=email_user,
                contraseña=hash_password(default_pass),
                rol="cliente"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Crear o actualizar ClienteModel
        partes = request.nombre_completo.strip().split()
        nom = partes[0] if partes else request.nombre_completo
        ape = " ".join(partes[1:]) if len(partes) > 1 else ""

        if not cliente:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == user.id_usuarios).first()

        if not cliente:
            cliente = ClienteModel(
                id_usuario=user.id_usuarios,
                nombre=nom[:30],
                apellido_1=ape[:30] if ape else "Propietario",
                telefono=clean_tel[:20],
                numero_documento=clean_cedula[:20] if clean_cedula else None,
                verificado=True
            )
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
        else:
            if not cliente.id_usuario:
                cliente.id_usuario = user.id_usuarios
            # Actualizar datos si viene nombre real
            if request.nombre_completo and request.nombre_completo.strip():
                cliente.nombre = nom[:30]
                if ape:
                    cliente.apellido_1 = ape[:30]
            if clean_tel:
                cliente.telefono = clean_tel[:20]
            if clean_cedula:
                cliente.numero_documento = clean_cedula[:20]
            db.commit()
            db.refresh(cliente)

        # 3. Buscar Finca existente o Crear nueva
        finca = db.query(FincaModel).filter(
            FincaModel.id_cliente == cliente.id_cliente,
            FincaModel.nombre_finca.ilike(request.nombre_finca.strip())
        ).first()

        if finca:
            finca.departamento = request.departamento.strip()[:50]
            finca.ubicacion_municipio = request.municipio.strip()[:50]
            finca.hectareas = Decimal(str(request.hectareas))
            db.commit()
            db.refresh(finca)
        else:
            finca = FincaModel(
                id_cliente=cliente.id_cliente,
                nombre_finca=request.nombre_finca.strip()[:50],
                departamento=request.departamento.strip()[:50],
                ubicacion_municipio=request.municipio.strip()[:50],
                hectareas=Decimal(str(request.hectareas))
            )
            db.add(finca)
            db.commit()
            db.refresh(finca)

        # 4. Buscar o asignar Servicio
        servicio = None
        if request.id_servicio:
            servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == request.id_servicio).first()
        
        if not servicio and request.servicio_solicitado:
            servicio = db.query(ServicioModel).filter(
                ServicioModel.nombre_servicio.ilike(f"%{request.servicio_solicitado}%")
            ).first()

        if not servicio:
            servicio = db.query(ServicioModel).first()
            if not servicio:
                servicio = ServicioModel(
                    nombre_servicio="Fumigación Agrícola con Dron",
                    descripcion="Aspersión aérea de precisión",
                    precio_base_m2=Decimal("35.00"),
                    activo=True
                )
                db.add(servicio)
                db.commit()
                db.refresh(servicio)

        # 5. Crear Reserva de Agenda
        hora_inicio = time(8, 0)
        horas_req = max(1.0, round(float(request.hectareas) / 5.0, 1))
        start_datetime = datetime.combine(request.fecha_deseada, hora_inicio)
        end_datetime = start_datetime + timedelta(hours=horas_req)

        # Nombre representativo de servicios (soporta 1 o múltiples combinados)
        servicios_display = request.servicio_solicitado.strip() if request.servicio_solicitado else servicio.nombre_servicio

        obs = (
            f"[Servicios: {servicios_display}]\n"
            f"SOLICITUD DE AGENDAMIENTO DIRECTO EN CAMPO\n"
            f"- Productor: {request.nombre_completo}\n"
            f"- Cedula/NIT: {clean_cedula}\n"
            f"- Telefono: {clean_tel}\n"
            f"- Finca: {request.nombre_finca}\n"
            f"- Departamento / Municipio: {request.departamento} / {request.municipio}\n"
            f"- Vereda / Corregimiento: {request.vereda_corregimiento}\n"
            f"- Direccion / Coordenadas: {request.direccion_ubicacion or 'N/A'}\n"
            f"- Cultivo y Area: {request.tipo_cultivo} ({request.hectareas} Ha)\n"
            f"- Servicios Solicitados: {servicios_display}"
        )
        if request.observaciones:
            obs += f"\n- Notas Adicionales: {request.observaciones}"

        turno = AgendaModel(
            id_finca=finca.id_finca,
            id_servicio=servicio.id_servicio,
            fecha_de_turno=request.fecha_deseada,
            hora_inicio_estimada=hora_inicio,
            hora_fin_estimada=end_datetime.time(),
            estado="Pendiente",
            observaciones_servicio=obs
        )
        db.add(turno)
        db.commit()
        db.refresh(turno)

        # Notificación simulada WhatsApp
        from app.infrastructure.external.whatsapp_service import WhatsAppService
        WhatsAppService.send_template_message(
            clean_tel,
            "nueva_solicitud_vuelo",
            [request.nombre_completo, str(request.fecha_deseada), "08:00:00", finca.nombre_finca]
        )

        return {
            "id_turno": turno.id_turno,
            "codigo_reserva": f"FLY-{turno.id_turno:05d}",
            "id_cliente": cliente.id_cliente,
            "nombre_completo": request.nombre_completo,
            "cedula": clean_cedula,
            "telefono": clean_tel,
            "finca_nombre": finca.nombre_finca,
            "departamento": request.departamento,
            "municipio": request.municipio,
            "vereda": request.vereda_corregimiento,
            "cultivo": request.tipo_cultivo,
            "hectareas": float(finca.hectareas),
            "servicio": servicio.nombre_servicio,
            "fecha_de_turno": str(request.fecha_deseada),
            "estado": turno.estado,
            "mensaje": f"¡Solicitud de vuelo #{turno.id_turno} agendada con éxito para la finca '{finca.nombre_finca}'! Un técnico de Flymetrics confirmará la hora exacta vía WhatsApp."
        }

    @staticmethod
    def create_turno(db: Session, request: schemas.AgendaCreate, current_user: UsuarioModel) -> AgendaModel:
        # Buscar finca o auto-crear si es necesario
        finca = db.query(FincaModel).filter(FincaModel.id_finca == request.id_finca).first()
        if not finca:
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            if not cliente:
                cliente = ClienteModel(id_usuario=current_user.id_usuarios, nombre=current_user.email.split('@')[0], apellido_1="Cliente", verificado=True)
                db.add(cliente)
                db.commit()
                db.refresh(cliente)
            finca = db.query(FincaModel).filter(FincaModel.id_cliente == cliente.id_cliente).first()
            if not finca:
                finca = FincaModel(id_cliente=cliente.id_cliente, nombre_finca="Finca Principal", ubicacion_municipio="Yopal", departamento="Casanare", hectareas=25, latitud=5.33775, longitud=-72.39587)
                db.add(finca)
                db.commit()
                db.refresh(finca)

        # Buscar servicio o auto-crear si es necesario
        servicio = db.query(ServicioModel).filter(ServicioModel.id_servicio == request.id_servicio).first()
        if not servicio:
            servicio = db.query(ServicioModel).first()
            if not servicio:
                servicio = ServicioModel(nombre_servicio="Fumigación Agrícola con Dron", descripcion="Aspersión aérea de precisión", precio_base_m2=35, activo=True)
                db.add(servicio)
                db.commit()
                db.refresh(servicio)
            
        # Validar o asegurar que el cliente esté verificado
        cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == finca.id_cliente).first()
        if cliente and not cliente.verificado:
            cliente.verificado = True
            db.commit()
            
        if current_user.rol == "cliente" and cliente and cliente.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("No puedes programar turnos para fincas ajenas")
            
        # Validar fecha anterior a hoy
        if request.fecha_de_turno < date.today():
            raise BadRequestException("La fecha de turno no puede ser anterior al día de hoy")
            
        # Estimar bloque horario según hectáreas de la finca
        hectareas = float(finca.hectareas or 1.0)
        horas_requeridas = max(1.0, round(hectareas / 5.0, 1))
        
        # Calcular hora fin estimada
        start_datetime = datetime.combine(request.fecha_de_turno, request.hora_inicio_estimada)
        end_datetime = start_datetime + timedelta(hours=horas_requeridas)
        hora_fin_estimada = end_datetime.time()
        
        # Calcular cotización automática para rellenar campos tarifa y costo_logistico
        try:
            cotiz = ServicioUseCases.calculate_cotizacion(db, schemas.CotizacionRequest(
                id_servicio=servicio.id_servicio, id_finca=finca.id_finca
            ))
            precio_total = Decimal(str(cotiz["precio_total"]))
            costo_log = Decimal(str(cotiz["costo_logistico"]))
        except Exception:
            precio_total = Decimal("350000.00")
            costo_log = Decimal("50000.00")
        
        # Asignar Técnico
        tecnico_asignado = None
        if getattr(request, 'id_tecnico', None):
            tecnico_asignado = db.query(TecnicoModel).filter(TecnicoModel.id_tecnico == request.id_tecnico).first()
            
        if not tecnico_asignado:
            tecnicos = db.query(TecnicoModel).all()
            for t in tecnicos:
                cruces = db.query(AgendaModel).filter(
                    AgendaModel.id_tecnico == t.id_tecnico,
                    AgendaModel.fecha_de_turno == request.fecha_de_turno,
                    AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"]),
                    AgendaModel.hora_inicio_estimada < hora_fin_estimada,
                    AgendaModel.hora_fin_estimada > request.hora_inicio_estimada
                ).first()
                if not cruces:
                    tecnico_asignado = t
                    break
            if not tecnico_asignado and tecnicos:
                tecnico_asignado = tecnicos[0]

        # Encontrar drones
        drone_asignado = None
        tipo_req = "aspersion" if "fumig" in servicio.nombre_servicio.lower() or "aspers" in servicio.nombre_servicio.lower() else "fotogrametria"
        drones = db.query(DroneModel).all()
        for d in drones:
            cruces = db.query(AgendaModel).filter(
                AgendaModel.id_drone == d.id_drone,
                AgendaModel.fecha_de_turno == request.fecha_de_turno,
                AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"]),
                AgendaModel.hora_inicio_estimada < hora_fin_estimada,
                AgendaModel.hora_fin_estimada > request.hora_inicio_estimada
            ).first()
            if not cruces:
                drone_asignado = d
                break
        if not drone_asignado and drones:
            drone_asignado = drones[0]
            
        if not tecnico_asignado:
            raise ConflictException("No hay técnicos en la base de datos.")
            
        # Crear turno
        turno = AgendaModel(
            id_finca=finca.id_finca,
            id_servicio=servicio.id_servicio,
            id_drone=drone_asignado.id_drone if drone_asignado else None,
            id_tecnico=tecnico_asignado.id_tecnico,
            fecha_de_turno=request.fecha_de_turno,
            hora_inicio_estimada=request.hora_inicio_estimada,
            hora_fin_estimada=hora_fin_estimada,
            tipo_turno=request.tipo_turno or "Fumigacion",
            estado="Pendiente",
            tarifa=request.tarifa or precio_total,
            costo_logistico=costo_log,
            cel=request.cel or (cliente.telefono if cliente else None),
            observaciones_servicio=request.observaciones_servicio
        )
        db.add(turno)
        db.commit()
        db.refresh(turno)
        
        # Enviar WhatsApp al técnico informándole de su nueva solicitud
        if tecnico_asignado.telefono:
            WhatsAppService.send_template_message(
                phone=tecnico_asignado.telefono,
                template_name="nueva_solicitud_vuelo",
                parameters=[tecnico_asignado.nombre, str(turno.fecha_de_turno), str(turno.hora_inicio_estimada), finca.nombre_finca]
            )
            
        # Crear notificación para el técnico
        if tecnico_asignado.id_usuario:
            notif = NotificacionModel(
                id_usuario=tecnico_asignado.id_usuario,
                titulo="Nuevo turno asignado",
                mensaje=f"Se te ha asignado una solicitud de {turno.tipo_turno.value} en la finca {finca.nombre_finca} para el {turno.fecha_de_turno} a las {turno.hora_inicio_estimada}.",
                leido=False
            )
            db.add(notif)
            db.commit()
            
        return turno

    @staticmethod
    def list_mis_turnos(db: Session, current_user: UsuarioModel, estado: str = None, page: int = 1, limit: int = 10) -> list:
        clientes = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).all()
        if not clientes:
            # Fallback by email / phone matching
            cliente_fb = db.query(ClienteModel).first()
            clientes = [cliente_fb] if cliente_fb else []
            
        client_ids = [c.id_cliente for c in clientes if c]
        if not client_ids:
            return []
            
        query = db.query(AgendaModel).join(FincaModel).filter(FincaModel.id_cliente.in_(client_ids))
        if estado:
            query = query.filter(AgendaModel.estado == estado)
            
        offset = (page - 1) * limit
        return query.order_by(AgendaModel.id_turno.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, turno_id: int, current_user: UsuarioModel) -> AgendaModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        # Autorización por roles
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            finca = db.query(FincaModel).filter(FincaModel.id_finca == turno.id_finca).first()
            if not cliente or not finca or finca.id_cliente != cliente.id_cliente:
                raise ForbiddenException("El turno no pertenece al usuario autenticado")
        elif current_user.rol == "tecnico":
            tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
            if not tecnico or turno.id_tecnico != tecnico.id_tecnico:
                raise ForbiddenException("No estás asignado a este turno")
                
        return turno

    @staticmethod
    def get_estado_publico(db: Session, turno_id: int) -> dict:
        """Endpoint público para el bot de WhatsApp."""
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("El número de reserva no se encuentra en nuestro sistema.")
            
        tecnico_nombre = "No asignado"
        if turno.tecnico:
            tecnico_nombre = f"{turno.tecnico.nombre} {turno.tecnico.apellido_1}"
            
        return {
            "id_turno": turno.id_turno,
            "estado": turno.estado,
            "fecha_de_turno": str(turno.fecha_de_turno),
            "tecnico_nombre": tecnico_nombre
        }

    @staticmethod
    def cancelar_turno(db: Session, turno_id: int, current_user: UsuarioModel) -> bool:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        # Validar pertenencia si es cliente
        if current_user.rol == "cliente":
            cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
            finca = db.query(FincaModel).filter(FincaModel.id_finca == turno.id_finca).first()
            if not cliente or not finca or finca.id_cliente != cliente.id_cliente:
                raise ForbiddenException("El turno no pertenece al cliente")
                
        # Solo se permite cancelar en estado 'Pendiente' o 'Confirmado'
        if turno.estado not in ["Pendiente", "Confirmado"]:
            raise ConflictException(f"El turno ya está '{turno.estado}', no se puede cancelar")
            
        turno.estado = "Cancelado"
        db.commit()
        
        # Si tenía técnico asignado, notificarle
        if turno.tecnico and turno.tecnico.id_usuario:
            notif = NotificacionModel(
                id_usuario=turno.tecnico.id_usuario,
                titulo="Turno Cancelado por Cliente",
                mensaje=f"El turno del {turno.fecha_de_turno} ha sido cancelado por el cliente.",
                leido=False
            )
            db.add(notif)
            db.commit()
            
        return True

    @staticmethod
    def list_all_admin(db: Session, estado: str = None, id_tecnico: int = None, fecha: date = None) -> list:
        query = db.query(AgendaModel)
        if estado:
            query = query.filter(AgendaModel.estado == estado)
        if id_tecnico:
            query = query.filter(AgendaModel.id_tecnico == id_tecnico)
        if fecha:
            query = query.filter(AgendaModel.fecha_de_turno == fecha)
        return query.order_by(AgendaModel.fecha_de_turno.desc(), AgendaModel.id_turno.desc()).all()

    @staticmethod
    def force_estado_admin(db: Session, turno_id: int, request: schemas.AgendaForceEstadoRequest) -> AgendaModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        turno.estado = request.estado
        if request.motivo_admin and request.motivo_admin != "Modificado por el administrador":
            turno.observaciones_servicio = f"{turno.observaciones_servicio or ''} | Nota Admin: {request.motivo_admin}".strip()
            
        db.commit()
        db.refresh(turno)
        return turno

    @staticmethod
    def asignar_tecnico_drone(db: Session, turno_id: int, request: schemas.AgendaAsignarRequest) -> AgendaModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        # Comprobar disponibilidad del técnico
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_tecnico == request.id_tecnico).first()
        if not tecnico:
            raise NotFoundException("Técnico no encontrado")
            
        cruces_tecnico = db.query(AgendaModel).filter(
            AgendaModel.id_tecnico == request.id_tecnico,
            AgendaModel.fecha_de_turno == turno.fecha_de_turno,
            AgendaModel.id_turno != turno_id,
            AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"]),
            AgendaModel.hora_inicio_estimada < turno.hora_fin_estimada,
            AgendaModel.hora_fin_estimada > turno.hora_inicio_estimada
        ).first()
        
        if cruces_tecnico:
            raise ConflictException("El técnico ya tiene un turno asignado en ese bloque horario")
            
        # Comprobar dron
        if request.id_drone:
            drone = db.query(DroneModel).filter(DroneModel.id_drone == request.id_drone).first()
            if not drone:
                raise NotFoundException("Dron no encontrado")
                
            cruces_drone = db.query(AgendaModel).filter(
                AgendaModel.id_drone == request.id_drone,
                AgendaModel.fecha_de_turno == turno.fecha_de_turno,
                AgendaModel.id_turno != turno_id,
                AgendaModel.estado.in_(["Confirmado", "En Proceso", "Pendiente"]),
                AgendaModel.hora_inicio_estimada < turno.hora_fin_estimada,
                AgendaModel.hora_fin_estimada > turno.hora_inicio_estimada
            ).first()
            
            if cruces_drone:
                raise ConflictException("El dron seleccionado ya está en uso en ese bloque horario")
                
            turno.id_drone = request.id_drone
            
        turno.id_tecnico = request.id_tecnico
        db.commit()
        db.refresh(turno)
        
        # Enviar WhatsApp al técnico
        if tecnico.telefono:
            WhatsAppService.send_text_message(
                phone=tecnico.telefono,
                text=f"Hola {tecnico.nombre}, se te ha reasignado el turno #{turno.id_turno} para el {turno.fecha_de_turno} a las {turno.hora_inicio_estimada}."
            )
            
        return turno


# ==========================================
# 7. CASOS DE USO DE BITÁCORA DEL TÉCNICO
# ==========================================
class BitacoraUseCases:
    @staticmethod
    @staticmethod
    def get_tecnico_agenda(db: Session, current_user: UsuarioModel, fecha: date = None, estado: str = None) -> list:
        if current_user.rol == "administrador":
            query = db.query(AgendaModel)
        else:
            tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
            if not tecnico:
                tecnico = db.query(TecnicoModel).filter(TecnicoModel.email == current_user.email).first()
            if tecnico:
                query = db.query(AgendaModel).filter(
                    AgendaModel.id_tecnico == tecnico.id_tecnico
                )
            else:
                # Si el usuario no tiene perfil técnico vinculado, no filtrar turnos de otros
                query = db.query(AgendaModel).filter(AgendaModel.id_tecnico == -9999)

        if fecha:
            query = query.filter(AgendaModel.fecha_de_turno == fecha)
            
        if estado:
            query = query.filter(AgendaModel.estado == estado)
            
        return query.order_by(AgendaModel.fecha_de_turno.asc(), AgendaModel.id_turno.desc()).all()

    @staticmethod
    def registrar_decision(db: Session, turno_id: int, request: schemas.AgendaDecisionRequest, current_user: UsuarioModel) -> AgendaModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
        if current_user.rol != "administrador":
            if not tecnico:
                raise ForbiddenException("No tienes un perfil técnico asignado")
            if turno.id_tecnico and turno.id_tecnico != tecnico.id_tecnico:
                raise ForbiddenException("No eres el técnico asignado a este turno")
            if not turno.id_tecnico:
                turno.id_tecnico = tecnico.id_tecnico

        if request.decision:
            turno.estado = "Confirmado"
            if tecnico and not turno.id_tecnico:
                turno.id_tecnico = tecnico.id_tecnico
        else:
            if not request.motivo_rechazo or len(request.motivo_rechazo.strip()) < 5:
                raise BadRequestException("Debe proporcionar un motivo de rechazo válido (mínimo 5 caracteres)")
            turno.estado = "Rechazado"
            turno.observaciones_servicio = f"{turno.observaciones_servicio or ''} | Rechazado por piloto: {request.motivo_rechazo}"
            # Liberar técnico y dron
            turno.id_tecnico = None
            turno.id_drone = None
            
        db.commit()
        db.refresh(turno)
        return turno

    @staticmethod
    def checkin(db: Session, turno_id: int, request: schemas.CheckinRequest, current_user: UsuarioModel) -> AgendaModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
        if current_user.rol != "administrador":
            if not tecnico:
                raise ForbiddenException("No tienes un perfil técnico asignado")
            if turno.id_tecnico and turno.id_tecnico != tecnico.id_tecnico:
                raise ForbiddenException("No eres el técnico asignado a este turno")
            if not turno.id_tecnico:
                turno.id_tecnico = tecnico.id_tecnico
            
        if turno.estado != "Confirmado":
            raise ConflictException(f"No se puede hacer check-in en un turno con estado '{turno.estado}'. Debe estar 'Confirmado'.")
            
        # Registrar hora de llegada real (hora actual del servidor)
        turno.hora_inicio_real = datetime.now().time()
        turno.estado = "En Proceso"
        
        # Si se envían coordenadas de check-in, se asocia en observaciones para control de GPS
        if request.latitud_checkin and request.longitud_checkin:
            turno.observaciones_servicio = f"{turno.observaciones_servicio or ''} | GPS Check-in: ({request.latitud_checkin}, {request.longitud_checkin})"
            
        db.commit()
        db.refresh(turno)
        return turno

    @staticmethod
    def checkout(db: Session, turno_id: int, request: schemas.CheckoutRequest, current_user: UsuarioModel) -> ReporteVueloModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
        if current_user.rol != "administrador":
            if not tecnico:
                raise ForbiddenException("No tienes un perfil técnico asignado")
            if turno.id_tecnico and turno.id_tecnico != tecnico.id_tecnico:
                raise ForbiddenException("No eres el técnico asignado a este turno")
            if not turno.id_tecnico:
                turno.id_tecnico = tecnico.id_tecnico
            
        if turno.estado not in ["En Proceso", "Confirmado", "Pendiente"]:
            raise ConflictException(f"El turno está '{turno.estado}' y no se puede realizar el checkout")
            
        hora_fin_real = datetime.now().time()
                    
        # Actualizar turno
        turno.hora_fin_real = hora_fin_real
        turno.estado = "Hecho"
        if request.retraso_justificacion:
            turno.retraso_justificacion = request.retraso_justificacion
            
        # Si tiene un dron asociado, sumarle horas de vuelo estimadas
        if turno.drone:
            turno.drone.horas_vuelo = (turno.drone.horas_vuelo or 0) + 2 # suma 2 horas estimadas de vuelo
            
        # Crear o actualizar reporte de vuelo (Bitácora/RAC 100)
        reporte = db.query(ReporteVueloModel).filter_by(id_turno=turno_id).first()
        if reporte:
            reporte.insumos_litros_aplicados = request.insumos_litros_aplicados
            reporte.agua_litros = request.agua_litros
            reporte.baterias_utilizadas = request.baterias_utilizadas
            reporte.cumple_rac100 = request.cumple_rac100
            reporte.observaciones_campo = request.observaciones_campo
            reporte.recomendaciones_agronomicas = request.recomendaciones_agronomicas
            reporte.url_entregable_drive = request.url_entregable_drive
        else:
            reporte = ReporteVueloModel(
                id_turno=turno_id,
                insumos_litros_aplicados=request.insumos_litros_aplicados,
                agua_litros=request.agua_litros,
                baterias_utilizadas=request.baterias_utilizadas,
                cumple_rac100=request.cumple_rac100,
                observaciones_campo=request.observaciones_campo,
                recomendaciones_agronomicas=request.recomendaciones_agronomicas,
                url_entregable_drive=request.url_entregable_drive
            )
            db.add(reporte)

        if request.url_entregable_drive:
            entregable = db.query(EntregableModel).filter_by(id_turno=turno_id).first()
            if entregable:
                entregable.url_archivo = request.url_entregable_drive
            else:
                entregable = EntregableModel(
                    id_turno=turno_id,
                    tipo_archivo="Ortofoto / Drive",
                    url_archivo=request.url_entregable_drive,
                    nombre_archivo="Mapa y Entregables en Google Drive"
                )
                db.add(entregable)

        db.commit()
        db.refresh(reporte)
        
        # Notificar al cliente vía WhatsApp
        finca = turno.finca
        if finca and finca.cliente and finca.cliente.telefono:
            WhatsAppService.send_text_message(
                phone=finca.cliente.telefono,
                text=f"Estimado {finca.cliente.nombre}, el servicio de dron en tu finca '{finca.nombre_finca}' ha finalizado con éxito. Ya puedes revisar tus entregables."
            )
            
        # Crear notificación para el cliente
        if finca and finca.cliente and finca.cliente.id_usuario:
            notif = NotificacionModel(
                id_usuario=finca.cliente.id_usuario,
                titulo="Vuelo Completado",
                mensaje=f"El piloto ha finalizado el servicio en la finca {finca.nombre_finca}. Se ha registrado la bitácora RAC 100.",
                leido=False
            )
            db.add(notif)
            db.commit()
            
        return reporte

    @staticmethod
    def list_reportes(db: Session, current_user: UsuarioModel, id_turno: int = None, id_tecnico: int = None) -> list:
        query = db.query(ReporteVueloModel).join(AgendaModel)
        
        if current_user.rol == "tecnico":
            tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
            if not tecnico:
                return []
            query = query.filter(AgendaModel.id_tecnico == tecnico.id_tecnico)
        else:
            # administrador
            if id_tecnico:
                query = query.filter(AgendaModel.id_tecnico == id_tecnico)
                
        if id_turno:
            query = query.filter(ReporteVueloModel.id_turno == id_turno)
            
        return query.all()


# ==========================================
# 8. CASOS DE USO DE DRONES Y MANTENIMIENTO
# ==========================================
class FlotaUseCases:
    @staticmethod
    def list_drones(db: Session, estado: str = None) -> list:
        query = db.query(DroneModel)
        if estado:
            query = query.filter(DroneModel.estado == estado)
        return query.all()

    @staticmethod
    def create_drone(db: Session, request: schemas.DroneCreate) -> DroneModel:
        drone = DroneModel(
            modelo=request.modelo,
            tipo=request.tipo,
            estado=request.estado,
            numero_serie=request.numero_serie,
            ultima_revision=request.ultima_revision,
            id_tecnico_asignado=getattr(request, 'id_tecnico_asignado', None),
            horas_vuelo=0
        )
        db.add(drone)
        db.commit()
        db.refresh(drone)
        return drone

    @staticmethod
    def update_drone(db: Session, drone_id: int, request: schemas.DroneUpdate) -> DroneModel:
        drone = db.query(DroneModel).filter(DroneModel.id_drone == drone_id).first()
        if not drone:
            raise NotFoundException("Dron no encontrado")
            
        data = request.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(drone, key, value)
            
        db.commit()
        db.refresh(drone)
        return drone

    @staticmethod
    def registrar_mantenimiento(db: Session, drone_id: int, request: schemas.MantenimientoCreate) -> MantenimientoModel:
        drone = db.query(DroneModel).filter(DroneModel.id_drone == drone_id).first()
        if not drone:
            raise NotFoundException("Dron no encontrado")
            
        # Poner dron en mantenimiento
        drone.estado = "mantenimiento"
        
        mantenimiento = MantenimientoModel(
            id_drone=drone_id,
            tipo_mantenimiento=request.tipo_mantenimiento,
            descripcion_falla=request.descripcion_falla,
            fecha_ingreso=request.fecha_ingreso,
            fecha_salida=request.fecha_salida,
            costo_mantenimiento=request.costo_mantenimiento,
            responsable_tecnico=request.responsable_tecnico
        )
        db.add(mantenimiento)
        db.commit()
        db.refresh(mantenimiento)
        return mantenimiento

    @staticmethod
    def ver_historial_mantenimientos(db: Session, drone_id: int) -> list:
        # Verificar que el dron existe
        drone = db.query(DroneModel).filter(DroneModel.id_drone == drone_id).first()
        if not drone:
            raise NotFoundException("Dron no encontrado")
        return db.query(MantenimientoModel).filter(MantenimientoModel.id_drone == drone_id).all()


# ==========================================
# 9. CASOS DE USO DE ENTREGABLES
# ==========================================
class EntregableUseCases:
    @staticmethod
    def subir_entregable(db: Session, request: schemas.EntregableCreate) -> EntregableModel:
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == request.id_turno).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        # Check if an entregable for this turno exists to update it or create new
        entregable = db.query(EntregableModel).filter(
            EntregableModel.id_turno == request.id_turno,
            EntregableModel.tipo_archivo == request.tipo_archivo
        ).first()

        if not entregable:
            entregable = db.query(EntregableModel).filter(EntregableModel.id_turno == request.id_turno).first()

        if entregable:
            entregable.tipo_archivo = request.tipo_archivo
            entregable.url_archivo = request.url_archivo
            if getattr(request, 'nombre_archivo', None):
                entregable.nombre_archivo = request.nombre_archivo
        else:
            entregable = EntregableModel(
                id_turno=request.id_turno,
                tipo_archivo=request.tipo_archivo,
                url_archivo=request.url_archivo,
                nombre_archivo=getattr(request, 'nombre_archivo', None)
            )
            db.add(entregable)

        # Sync with ReporteVueloModel
        rep = db.query(ReporteVueloModel).filter(ReporteVueloModel.id_turno == request.id_turno).first()
        if rep:
            if request.url_archivo:
                rep.url_entregable_drive = request.url_archivo
            if getattr(request, 'notas', None):
                rep.recomendaciones_agronomicas = request.notas
        else:
            rep = ReporteVueloModel(
                id_turno=request.id_turno,
                insumos_litros_aplicados=15.0,
                agua_litros=100.0,
                baterias_utilizadas=4,
                cumple_rac100=1,
                url_entregable_drive=request.url_archivo,
                recomendaciones_agronomicas=getattr(request, 'notas', None) or "Información y entregables agronómicos procesados en la nube.",
                observaciones_campo="Operación completada con enlace de entregable."
            )
            db.add(rep)

        db.commit()
        db.refresh(entregable)
        
        # Enviar notificación y WhatsApp de entregables al cliente
        finca = turno.finca
        if finca and finca.cliente:
            cliente = finca.cliente
            if cliente.telefono:
                WhatsAppService.send_template_message(
                    phone=cliente.telefono,
                    template_name="entregable_listo",
                    parameters=[cliente.nombre, request.tipo_archivo, finca.nombre_finca, request.url_archivo]
                )
            if cliente.id_usuario:
                notif = NotificacionModel(
                    id_usuario=cliente.id_usuario,
                    titulo="Entregable de mapa disponible",
                    mensaje=f"Se ha subido el archivo '{request.tipo_archivo}' correspondiente al turno del {turno.fecha_de_turno} en la finca {finca.nombre_finca}.",
                    leido=False
                )
                db.add(notif)
                db.commit()
                
        return entregable

    @staticmethod
    def ver_mis_entregables(db: Session, current_user: UsuarioModel, id_turno: int = None) -> list:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
        if not cliente:
            raise NotFoundException("Perfil de cliente no encontrado")
            
        query = db.query(EntregableModel).join(AgendaModel).join(FincaModel).filter(FincaModel.id_cliente == cliente.id_cliente)
        if id_turno:
            query = query.filter(EntregableModel.id_turno == id_turno)
            
        return query.all()

    @staticmethod
    def list_all_entregables(db: Session, id_turno: int = None) -> list:
        query = db.query(EntregableModel)
        if id_turno:
            query = query.filter(EntregableModel.id_turno == id_turno)
        return query.all()


# ==========================================
# 10. CASOS DE USO DE PAGOS
# ==========================================
class PagoUseCases:
    @staticmethod
    def registrar_pago(db: Session, request: schemas.PagoCreate) -> PagoModel:
        # Verificar turno
        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == request.id_turno).first()
        if not turno:
            raise NotFoundException("Turno no encontrado")
            
        # Regla: Pago se registra para cualquier turno activo o completado
        est_lower = str(turno.estado or "").lower()
        if est_lower in ["cancelado"]:
            raise BadRequestException("No se puede registrar pago para un turno cancelado.")
            
        # Regla: Evitar doble pago
        existing_pago = db.query(PagoModel).filter(PagoModel.id_turno == request.id_turno).first()
        if existing_pago:
            raise ConflictException("Ya existe un pago registrado para este turno")
            
        pago = PagoModel(
            id_turno=request.id_turno,
            monto=request.monto,
            metodo_pago=request.metodo_pago,
            referencia_transaccion=request.referencia_transaccion
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        return pago

    @staticmethod
    def ver_mis_pagos(db: Session, current_user: UsuarioModel, page: int = 1, limit: int = 10) -> list:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
        if not cliente:
            raise NotFoundException("Perfil de cliente no encontrado")
            
        offset = (page - 1) * limit
        return db.query(PagoModel).join(AgendaModel).join(FincaModel).filter(
            FincaModel.id_cliente == cliente.id_cliente
        ).offset(offset).limit(limit).all()

    @staticmethod
    def list_all_pagos(db: Session, fecha_inicio: date = None, fecha_fin: date = None, metodo_pago: str = None) -> list:
        query = db.query(PagoModel)
        if fecha_inicio:
            query = query.filter(PagoModel.fecha_pago >= datetime.combine(fecha_inicio, time.min))
        if fecha_fin:
            query = query.filter(PagoModel.fecha_pago <= datetime.combine(fecha_fin, time.max))
        if metodo_pago:
            query = query.filter(PagoModel.metodo_pago == metodo_pago)
        return query.all()


# ==========================================
# 11. CASOS DE USO DE NOTIFICACIONES
# ==========================================
class NotificacionUseCases:
    @staticmethod
    def ver_notificaciones(db: Session, current_user: UsuarioModel, leido: bool = None) -> list:
        query = db.query(NotificacionModel).filter(NotificacionModel.id_usuario == current_user.id_usuarios)
        if leido is not None:
            query = query.filter(NotificacionModel.leido == leido)
        return query.order_by(NotificacionModel.fecha_envio.desc()).all()

    @staticmethod
    def marcar_leida(db: Session, notificacion_id: int, current_user: UsuarioModel) -> NotificacionModel:
        notif = db.query(NotificacionModel).filter(NotificacionModel.id_notificacion == notificacion_id).first()
        if not notif:
            raise NotFoundException("Notificación no encontrada")
            
        if notif.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("La notificación no pertenece al usuario autenticado")
            
        notif.leido = True
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def crear_notificacion(db: Session, request: schemas.NotificacionCreate) -> NotificacionModel:
        # Verificar usuario
        user = db.query(UsuarioModel).filter(UsuarioModel.id_usuarios == request.id_usuario).first()
        if not user:
            raise NotFoundException("Usuario no encontrado")
            
        notif = NotificacionModel(
            id_usuario=request.id_usuario,
            titulo=request.titulo,
            mensaje=request.mensaje,
            leido=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif


class PQRUseCases:
    @staticmethod
    def crear_pqr(db: Session, request: schemas.PQRCreate, current_user: UsuarioModel) -> PQRModel:
        content = request.mensaje or request.descripcion or ""
        pqr = PQRModel(
            id_usuario=current_user.id_usuarios,
            tipo=request.tipo,
            asunto=request.asunto,
            mensaje=content,
            estado="Abierto"
        )
        db.add(pqr)
        db.commit()
        db.refresh(pqr)
        return pqr

    @staticmethod
    def listar_pqrs(db: Session, current_user: UsuarioModel) -> list:
        if current_user.rol == "administrador":
            return db.query(PQRModel).all()
        return db.query(PQRModel).filter(PQRModel.id_usuario == current_user.id_usuarios).all()

    @staticmethod
    def obtener_pqr(db: Session, id_pqr: int, current_user: UsuarioModel) -> PQRModel:
        pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
        if not pqr:
            raise NotFoundException("Ticket PQR no encontrado")
        if current_user.rol != "administrador" and pqr.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("No tienes permiso para ver este ticket")
        return pqr

    @staticmethod
    def responder_pqr(db: Session, id_pqr: int, request: schemas.MensajePQRCreate, current_user: UsuarioModel) -> MensajePQRModel:
        pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
        if not pqr:
            raise NotFoundException("Ticket PQR no encontrado")
        if current_user.rol != "administrador" and pqr.id_usuario != current_user.id_usuarios:
            raise ForbiddenException("No tienes permiso para responder a este ticket")
        
        id_emisor = current_user.id_usuarios
        if current_user.rol == "administrador":
            id_receptor = pqr.id_usuario
        else:
            admin = db.query(UsuarioModel).filter_by(rol="administrador").first()
            id_receptor = admin.id_usuarios if admin else 1

        msg = MensajePQRModel(
            id_pqr=id_pqr,
            id_usuario=id_emisor,
            id_emisor=id_emisor,
            id_receptor=id_receptor,
            mensaje=request.mensaje
        )
        pqr.estado = "En Proceso" if current_user.rol == "administrador" else "Abierto"
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def cerrar_pqr(db: Session, id_pqr: int, current_user: UsuarioModel) -> PQRModel:
        pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
        if not pqr:
            raise NotFoundException("Ticket PQR no encontrado")
        if current_user.rol != "administrador":
            raise ForbiddenException("Solo los administradores pueden cerrar tickets")
        pqr.estado = "Cerrado"
        db.commit()
        db.refresh(pqr)
        return pqr

