from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import re

from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.models import UsuarioModel, ClienteModel, PQRModel, NotificacionModel
from app.infrastructure.security.jwt_handler import hash_password
from app.shared.responses.response import success_response
from app.presentation.api.dependencies.auth import RoleChecker, get_current_user

router = APIRouter(prefix="/contacto", tags=["Contacto Web (Público)"])
admin_required = RoleChecker(["administrador"])


class ContactoPublicoRequest(BaseModel):
    nombre: str
    telefono: str
    email: str
    tipo: Optional[str] = "Cotización de servicio"
    hectareas: Optional[float] = None
    cultivo: Optional[str] = None
    ubicacion: Optional[str] = None
    mensaje: Optional[str] = ""


@router.post("", status_code=status.HTTP_201_CREATED)
def recibir_contacto_web(
    request: ContactoPublicoRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint público (sin autenticación) para recibir solicitudes de cotización e información 24 horas
    desde la página de inicio. Guarda la solicitud en la base de datos (tabla_pqrs) y genera una notificación
    automática en la base de datos para todos los administradores del sistema.
    """
    # Intentar encontrar o crear usuario para el contacto
    usuario_sistema = db.query(UsuarioModel).filter(
        UsuarioModel.rol == "administrador"
    ).first()

    # Buscar si ya existe un usuario con ese email
    usuario_contacto = db.query(UsuarioModel).filter(
        UsuarioModel.email == request.email.strip().lower()
    ).first()

    # Si no existe, crear cuenta de cliente provisional
    if not usuario_contacto:
        try:
            usuario_contacto = UsuarioModel(
                email=request.email.strip().lower(),
                contraseña=hash_password(f"FM_ContactWeb_{datetime.now().strftime('%Y%m%d')}"),
                rol="cliente"
            )
            db.add(usuario_contacto)
            db.flush()

            # Crear perfil de cliente básico
            nombre_partes = request.nombre.strip().split(" ", 1)
            cliente = ClienteModel(
                id_usuario=usuario_contacto.id_usuarios,
                nombre=nombre_partes[0],
                apellido_1=nombre_partes[1] if len(nombre_partes) > 1 else "Contacto",
                telefono=request.telefono.strip(),
                verificado=False
            )
            db.add(cliente)
            db.flush()
        except Exception:
            db.rollback()
            usuario_contacto = usuario_sistema

    # ID de usuario asociado para el ticket
    id_usuario_pqr = usuario_contacto.id_usuarios if usuario_contacto else (
        usuario_sistema.id_usuarios if usuario_sistema else 1
    )

    ha_str = f"{request.hectareas} ha" if request.hectareas else "No especificado"
    cultivo_str = request.cultivo if request.cultivo else "No especificado"
    ubicacion_str = request.ubicacion if request.ubicacion else "No especificado"

    cuerpo_mensaje = (
        f"📋 SOLICITUD DE COTIZACIÓN 24 HORAS (DESDE LA PÁGINA WEB)\n\n"
        f"👤 Nombre: {request.nombre.strip()}\n"
        f"📱 Teléfono/WhatsApp: {request.telefono.strip()}\n"
        f"📧 Email: {request.email.strip()}\n"
        f"🌾 Hectáreas: {ha_str}\n"
        f"🌱 Cultivo: {cultivo_str}\n"
        f"📍 Ubicación/Municipio: {ubicacion_str}\n"
        f"🗂️ Servicio Requerido: {request.tipo}\n\n"
        f"💬 Mensaje / Consulta:\n{request.mensaje.strip() if request.mensaje else 'Sin mensaje adicional'}\n\n"
        f"---\n⏰ Recibido: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    pqr = PQRModel(
        id_usuario=id_usuario_pqr,
        tipo="Petición",
        asunto=f"[CONTACTO 24H] {request.tipo} — {request.nombre.strip()} ({ha_str})",
        mensaje=cuerpo_mensaje,
        estado="Abierto"
    )
    db.add(pqr)
    db.flush()

    # Notificar en la base de datos a todos los administradores
    admins = db.query(UsuarioModel).filter(UsuarioModel.rol == "administrador").all()
    for adm in admins:
        notif = NotificacionModel(
            id_usuario=adm.id_usuarios,
            titulo=f"📩 Nueva Cotización 24h: {request.nombre.strip()}",
            mensaje=f"Se ha recibido una nueva solicitud de {request.tipo} para {ha_str} de {cultivo_str}. Tel: {request.telefono}",
            leido=False
        )
        db.add(notif)

    db.commit()
    db.refresh(pqr)

    return success_response(
        message="¡Solicitud recibida! Un asesor de Flymetrics te contactará en menos de 24 horas.",
        data={
            "recibido": True,
            "id_ticket": pqr.id_pqr,
            "nombre": request.nombre,
            "email": request.email,
            "telefono": request.telefono,
            "hectareas": request.hectareas
        },
        status_code=201
    )


@router.get("/solicitudes", status_code=status.HTTP_200_OK)
def listar_solicitudes_contacto(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """
    Obtiene la lista de todas las solicitudes de contacto y cotización recibidas desde la landing page.
    """
    solicitudes = db.query(PQRModel).filter(
        (PQRModel.asunto.like("%[CONTACTO%")) | 
        (PQRModel.asunto.like("%Contacto%")) | 
        (PQRModel.asunto.like("%Solicitud%")) |
        (PQRModel.asunto.like("%Cotización%")) |
        (PQRModel.mensaje.like("%SOLICITUD%"))
    ).order_by(PQRModel.fecha_creacion.desc()).all()

    if not solicitudes:
        solicitudes = db.query(PQRModel).order_by(PQRModel.fecha_creacion.desc()).limit(30).all()
    
    result = []
    for p in solicitudes:
        txt = p.mensaje or ""
        # Extraer campos mediante regex si existen
        nombre_match = re.search(r"Nombre:\s*([^\n]+)", txt)
        tel_match = re.search(r"Teléfono/WhatsApp:\s*([^\n]+)", txt)
        email_match = re.search(r"Email:\s*([^\n]+)", txt)
        ha_match = re.search(r"Hectáreas:\s*([^\n]+)", txt)
        cultivo_match = re.search(r"Cultivo:\s*([^\n]+)", txt)
        ubicacion_match = re.search(r"Ubicación/Municipio:\s*([^\n]+)", txt)
        servicio_match = re.search(r"Servicio Requerido:\s*([^\n]+)", txt)
        msg_match = re.search(r"Mensaje / Consulta:\s*\n([^\n-]+)", txt)

        nombre = nombre_match.group(1).strip() if nombre_match else (p.usuario.cliente.nombre if (p.usuario and p.usuario.cliente) else "Contacto Web")
        telefono = tel_match.group(1).strip() if tel_match else (p.usuario.cliente.telefono if (p.usuario and p.usuario.cliente) else "")
        email = email_match.group(1).strip() if email_match else (p.usuario.email if p.usuario else "")
        hectareas = ha_match.group(1).strip() if ha_match else "—"
        cultivo = cultivo_match.group(1).strip() if cultivo_match else "—"
        ubicacion = ubicacion_match.group(1).strip() if ubicacion_match else "—"
        servicio = servicio_match.group(1).strip() if servicio_match else p.asunto
        mensaje_limpio = msg_match.group(1).strip() if msg_match else txt

        result.append({
            "id_pqr": p.id_pqr,
            "asunto": p.asunto,
            "nombre": nombre,
            "telefono": telefono,
            "email": email,
            "hectareas": hectareas,
            "cultivo": cultivo,
            "ubicacion": ubicacion,
            "servicio": servicio,
            "mensaje": mensaje_limpio,
            "mensaje_completo": txt,
            "estado": p.estado,
            "fecha": p.fecha_creacion.isoformat() if p.fecha_creacion else None,
            "respuesta": p.mensajes[0].mensaje if p.mensajes else None
        })

    return success_response(message="Solicitudes de contacto obtenidas exitosamente", data=result)


@router.patch("/solicitudes/{id_pqr}/estado", status_code=status.HTTP_200_OK)
def cambiar_estado_solicitud(
    id_pqr: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """
    Permite al administrador cambiar el estado de una solicitud (Abierto, En Proceso, Atendido, Cerrado).
    """
    pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
    if not pqr:
        from app.shared.exceptions.exceptions import NotFoundException
        raise NotFoundException("Solicitud no encontrada")
    
    nuevo_estado = request.get("estado", "Atendido")
    pqr.estado = nuevo_estado
    db.commit()
    db.refresh(pqr)
    return success_response(message=f"Estado de solicitud #{id_pqr} actualizado a '{nuevo_estado}'", data={"id_pqr": id_pqr, "estado": nuevo_estado})


@router.get("/solicitudes/{id_pqr}", status_code=status.HTTP_200_OK)
def detalle_solicitud_contacto(
    id_pqr: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """
    Obtiene el detalle de una solicitud de contacto específica.
    """
    pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
    if not pqr:
        from app.shared.exceptions.exceptions import NotFoundException
        raise NotFoundException("Solicitud no encontrada")
    return success_response(message="Detalle de solicitud obtenido", data={"id_pqr": pqr.id_pqr, "asunto": pqr.asunto, "mensaje": pqr.mensaje, "estado": pqr.estado})


@router.delete("/solicitudes/{id_pqr}", status_code=status.HTTP_200_OK)
def eliminar_solicitud_contacto(
    id_pqr: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_required)
):
    """
    Elimina permanentemente una solicitud de contacto por su id_pqr.
    """
    pqr = db.query(PQRModel).filter(PQRModel.id_pqr == id_pqr).first()
    if not pqr:
        from app.shared.exceptions.exceptions import NotFoundException
        raise NotFoundException("Solicitud no encontrada")
    
    db.delete(pqr)
    db.commit()
    return success_response(message=f"Solicitud de cotización #{id_pqr} eliminada permanentemente.", data={"id_pqr": id_pqr, "eliminado": True})



@router.get("/config/sistema", status_code=status.HTTP_200_OK)
def get_public_system_config(db: Session = Depends(get_db)):
    """
    Endpoint público para sincronización omnicanal de canales oficiales y plantillas de WhatsApp.
    """
    from app.infrastructure.database.models.models import SystemConfigModel
    import json
    config_record = db.query(SystemConfigModel).filter(SystemConfigModel.clave == "perfil_corporativo").first()
    data = json.loads(config_record.valor) if config_record and config_record.valor else {
        "empresa": "Flymetrics Colombia S.A.S.",
        "nit": "900.123.456-7",
        "telefono": "+57 315 542 9714",
        "whatsapp": "+57 315 542 9714",
        "email": "comercial@flymetrix.com.co",
        "direccion": "Avenida El Dorado #68b-70, Bogotá D.C.",
        "wa_template_24h": "Hola {nombre}, te contactamos desde Flymetrics Colombia sobre tu solicitud de {servicio} ({hectareas} ha).",
        "wa_template_agendar": "Hola Flymetrics Colombia, acabo de agendar una solicitud de servicio / demostración:\nRadicado: {radicado}\nProductor: {nombre} (CC/NIT: {cedula})\nFinca: {finca} en {municipio} ({departamento})\nCultivo: {cultivo} ({hectareas} Ha)\nServicio: {servicio}\nFecha programada: {fecha}\nUbicación / Maps: {ubicacion_maps}\nDeseo coordinar detalles técnicos de campo con el piloto.",
        "wa_template_general": "Hola Flymetrics, deseo solicitar asesoría e información técnica sobre sus servicios de drones agrícolas."
    }
    return success_response(message="Configuración corporativa obtenida exitosamente", data=data)


@router.post("/solicitar-soporte-facturacion", status_code=status.HTTP_200_OK)
def solicitar_soporte_facturacion(
    request: dict,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    """
    Registra automáticamente una solicitud de soporte / enlace de facturación Alegra en la base de datos (tabla_pqrs y notificaciones).
    """
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
    nombre_cli = f"{cliente.nombre} {cliente.apellido_1 or ''}".strip() if cliente else current_user.email
    cedula_cli = cliente.numero_documento if (cliente and cliente.numero_documento) else "No registrada"
    tel_cli = cliente.telefono if (cliente and cliente.telefono) else "No registrado"

    pqr = PQRModel(
        id_usuario=current_user.id_usuarios,
        tipo="Petición",
        asunto=f"[FACTURACIÓN ALEGRA] Solicitud de factura / portal para {nombre_cli}",
        mensaje=(
            f"📋 SOLICITUD DE FACTURACIÓN ELECTRÓNICA & INTEGRACIÓN ALEGRA\n\n"
            f"👤 Cliente: {nombre_cli}\n"
            f"🆔 CC / NIT: {cedula_cli}\n"
            f"📱 Teléfono: {tel_cli}\n"
            f"📧 Email: {current_user.email}\n"
            f"💬 Detalle: El cliente solicita vinculación y acceso directo a su facturación electrónica en Alegra.\n\n"
            f"---\n⏰ Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ),
        estado="Abierto"
    )
    db.add(pqr)

    # Notificar a administradores
    admins = db.query(UsuarioModel).filter(UsuarioModel.rol == "administrador").all()
    for adm in admins:
        notif = NotificacionModel(
            id_usuario=adm.id_usuarios,
            titulo=f"🧾 Solicitud Facturación Alegra: {nombre_cli}",
            mensaje=f"El cliente {nombre_cli} solicita vincular su cuenta o factura electrónica en Alegra.",
            leido=False
        )
        db.add(notif)

    db.commit()
    return success_response(message="Solicitud de facturación registrada exitosamente en la base de datos.", data={"id_pqr": pqr.id_pqr})


