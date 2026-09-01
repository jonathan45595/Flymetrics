from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
import re

from app.infrastructure.database.session import get_db
from app.infrastructure.config.settings import settings
from app.infrastructure.database.models.models import AgendaModel
from app.infrastructure.external.whatsapp_service import WhatsAppService
from app.shared.responses.response import success_response
from app.shared.exceptions.exceptions import ForbiddenException

router = APIRouter(prefix="/webhook", tags=["Chatbot WhatsApp (Meta API)"])

@router.get("/whatsapp")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificación GET requerido por Meta.
    Valida el token de verificación y retorna el challenge recibido.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        print("[WHATSAPP WEBHOOK] Verificación de Webhook exitosa.")
        # Retornar el challenge directamente como texto plano / entero para Meta
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        raise ForbiddenException("Token de verificación incorrecto o modo inválido")

@router.post("/whatsapp")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint POST para recibir mensajes de clientes enviados por Meta.
    Extrae la intención (ej: número de reserva) y responde automáticamente.
    """
    try:
        body = await request.json()
        print(f"[WHATSAPP WEBHOOK] Mensaje recibido: {body}")
        
        # Validar formato estándar de webhook de Meta
        if body.get("object") != "whatsapp_business_account":
            return success_response(message="Evento omitido (no es de cuenta business)", data={})
            
        entry_list = body.get("entry", [])
        for entry in entry_list:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for msg in messages:
                    sender_phone = msg.get("from")
                    text_obj = msg.get("text", {})
                    msg_body = text_obj.get("body", "").strip()
                    
                    if not sender_phone or not msg_body:
                        continue
                        
                    # Procesar mensaje. Buscar números (ej: id_turno)
                    # Expresión regular para buscar números de reserva
                    numbers = re.findall(r"\b\d+\b", msg_body)
                    
                    if numbers:
                        turno_id = int(numbers[0])
                        # Consultar el turno en base de datos
                        turno = db.query(AgendaModel).filter(AgendaModel.id_turno == turno_id).first()
                        
                        if turno:
                            tecnico_nombre = "No asignado aún"
                            if turno.tecnico:
                                tecnico_nombre = f"{turno.tecnico.nombre} {turno.tecnico.apellido_1}"
                                
                            reply = (
                                f"Hola, el estado de tu reserva #{turno.id_turno} es *{turno.estado}*.\n"
                                f"Detalles:\n"
                                f"- Fecha: {turno.fecha_de_turno}\n"
                                f"- Piloto asignado: {tecnico_nombre}\n"
                                f"- Servicio: {turno.servicio.nombre_servicio}\n"
                                f"- Finca: {turno.finca.nombre_finca}"
                            )
                        else:
                            reply = f"El número de reserva #{turno_id} no se encuentra en nuestro sistema."
                    else:
                        # Fallback con menú interactivo
                        reply = (
                            "¡Hola! Bienvenido al bot de Flymetrics Command Center. 🛸\n\n"
                            "Si deseas consultar el estado de tu servicio de drones, por favor escribe el número de tu reserva.\n"
                            "Ejemplo: *'Estado de mi turno 5'*\n\n"
                            "Para otras consultas, puedes comunicarte con soporte al (+57) 305 406 1764."
                        )
                        
                    # Enviar respuesta simulada a través de Meta
                    WhatsAppService.send_text_message(sender_phone, reply)
                    
        return success_response(message="Webhook procesado exitosamente")
    except Exception as e:
        print(f"[WHATSAPP WEBHOOK ERROR] Error procesando webhook: {e}")
        return success_response(message="Webhook recibido pero con fallos internos")
