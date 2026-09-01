import logging

logger = logging.getLogger("whatsapp_service")

class WhatsAppService:
    @classmethod
    def send_template_message(cls, phone: str, template_name: str, parameters: list) -> bool:
        """Simula el envío de un mensaje de plantilla de WhatsApp a través de Meta Cloud API."""
        if not phone:
            return False
            
        logger.info(
            f"[WHATSAPP MOCK] Enviando mensaje a {phone} usando plantilla '{template_name}'. "
            f"Parámetros: {parameters}"
        )
        print(
            f"--- WHATSAPP SENT TO {phone} ---\n"
            f"Plantilla: {template_name}\n"
            f"Contenido simulado con parámetros: {', '.join(map(str, parameters))}\n"
            f"--------------------------------"
        )
        return True

    @classmethod
    def send_text_message(cls, phone: str, text: str) -> bool:
        """Simula el envío de un mensaje de texto plano por WhatsApp."""
        if not phone:
            return False
            
        logger.info(f"[WHATSAPP MOCK] Enviando texto a {phone}: '{text}'")
        print(
            f"--- WHATSAPP TEXT TO {phone} ---\n"
            f"Mensaje: {text}\n"
            f"--------------------------------"
        )
        return True
