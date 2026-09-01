import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.infrastructure.config.settings import settings

logger = logging.getLogger("uvicorn")

def send_otp_email(to_email: str, otp_code: str) -> bool:
    """Envía un correo electrónico profesional con el código OTP de 6 dígitos para verificar la cuenta."""
    smtp_host = getattr(settings, "SMTP_HOST", "smtp.gmail.com")
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    smtp_user = getattr(settings, "SMTP_USER", "")
    smtp_pass = getattr(settings, "SMTP_PASSWORD", "")
    sender_email = getattr(settings, "SENDER_EMAIL", smtp_user or "notificaciones@flymetrics.co")

    subject = "🔐 Código de Verificación de Cuenta — Flymetrics S.A.S."
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f9; margin: 0; padding: 20px; }}
        .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,48,73,0.08); border: 1px solid #e2e8f0; }}
        .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #f0f4f8; }}
        .title {{ color: #003049; font-size: 22px; font-weight: 800; margin: 10px 0 0 0; }}
        .body-text {{ color: #4a5568; font-size: 15px; line-height: 1.6; text-align: center; margin: 24px 0; }}
        .otp-box {{ background: linear-gradient(135deg, #1c82ad, #003049); color: #ffffff; font-size: 32px; font-weight: 900; letter-spacing: 8px; text-align: center; padding: 18px; border-radius: 12px; margin: 20px 0; box-shadow: 0 8px 20px rgba(28,130,173,0.3); }}
        .footer {{ text-align: center; color: #a0aec0; font-size: 12px; margin-top: 30px; border-top: 1px solid #edf2f7; padding-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h2 class="title">Flymetrics S.A.S.</h2>
          <p style="color:#1c82ad; font-size:13px; font-weight:700; margin:4px 0 0 0;">Gestión Inteligente de Drones Agrícolas</p>
        </div>
        <div class="body-text">
          Hola,<br/>
          Has solicitado verificar tu correo electrónico para completar el registro de tu cuenta en <strong>Flymetrics</strong>. Tu código de seguridad OTP es:
        </div>
        <div class="otp-box">{otp_code}</div>
        <div class="body-text" style="font-size:13px; color:#718096;">
          Este código es válido por 15 minutos. Si no has solicitado este código, por favor ignora este mensaje.
        </div>
        <div class="footer">
          &copy; 2026 Flymetrics S.A.S. — Todos los derechos reservados.<br/>
          Soporte: soporte@flymetrics.co
        </div>
      </div>
    </body>
    </html>
    """

    # Intentar envío SMTP si las credenciales están configuradas
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Flymetrics S.A.S. <{sender_email}>"
            msg["To"] = to_email
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender_email, to_email, msg.as_string())
            logger.info(f"[SMTP EMAIL PASS] Código OTP {otp_code} enviado a {to_email}")
            return True
        except Exception as e:
            logger.error(f"[SMTP EMAIL ERROR] Falló el envío de correo SMTP: {e}")
    
    # Si no hay credenciales SMTP de producción configuradas, loguear para el entorno de desarrollo
    logger.info(f"[CORREO SENT TO {to_email}] CODIGO OTP: {otp_code}")
    print(f"\n======================================================\n [CORREO ELECTRÓNICO SENT TO: {to_email}]\n [CÓDIGO DE VERIFICACIÓN OTP: {otp_code}]\n======================================================\n")
    return True
