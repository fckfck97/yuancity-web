from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
import logging
import threading
import traceback

from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

def send_sms_in_background(to_number: str, body_text: str) -> None:
    """
    Versión mejorada con:
    - Validación de configuración
    - Manejo de errores robusto
    - Compatibilidad con modo prueba
    """
    def _send_sms():
        try:
            # 1. Validar configuración
            required_settings = [
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN',
                'TWILIO_PHONE_NUMBER'
            ]
            
            for setting in required_settings:
                if not getattr(settings, setting, None):
                    logger.error(f'Configuración faltante: {setting}')
                    return

            # 2. Validar número destino
            if not to_number.startswith('+'):
                logger.error(f'Número inválido: {to_number}')
                return
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            # 3. Inicializar cliente
            client = Client(account_sid, auth_token)

            # 4. Enviar mensaje
            message = client.messages.create(
                body=body_text[:160],
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )

            logger.info(f'SMS enviado a {to_number}. SID: {message.sid}')

        except TwilioRestException as e:
            logger.error(f'Error Twilio ({e.code}): {e.msg}')
        except Exception as e:
            logger.error(f'Error inesperado: {str(e)}')

    # Ejecutar en segundo plano
    threading.Thread(target=_send_sms, daemon=True).start()
    

def send_email_in_background(subject: str, body: str, to_email: str) -> None:
    """
    Envía un correo electrónico en segundo plano utilizando el CustomEmailBackend.
    """
    def _send_email():
        try:
            email_message = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )
            email_message.content_subtype = 'html'  # Esto indica que el contenido es HTML.
            email_message.send()
            logger.info(f'Correo enviado a {to_email} con asunto: {subject}')
        except Exception as e:
            logger.error(f'Error enviando correo a {to_email}: {str(e)}')
            traceback.print_exc()
    
    threading.Thread(target=_send_email, daemon=True).start()


def create_case_creation_email(user, case) -> tuple[str, str]:
    """
    Genera el asunto y cuerpo del correo para notificar la creación de un caso.
    Diferencia el mensaje según el rol (client o lawyer).
    """
    if user.rol == "client":
        subject = f"Hemos tomado tu caso #{case.id}"
        body = (
            f"<h3>Felicidades {user.get_full_name()}</h3>"
            f"<p>Hemos tomado tu caso en humanlaw. El abogado asignado se comunicará contigo pronto.</p>"
            f"<p><strong>Detalles del caso:</strong></p>"
            f"<ul>"
            f"<li><strong>Área:</strong> {case.area}</li>"
            f"<li><strong>Jurisdicción:</strong> {case.jurisdiction}</li>"
            f"<li><strong>Urgencia:</strong> {case.urgency}</li>"
            f"</ul>"
        )
    elif user.rol == "lawyer":
        subject = f"Nuevo caso asignado #{case.id} en humanlaw.ai"
        body = (
            f"<p>{user.get_full_name()}, se ha creado un caso en humanlaw.ai.</p>"
            f"<p><strong>Detalles del caso:</strong></p>"
            f"<ul>"
            f"<li><strong>Área:</strong> {case.area}</li>"
            f"<li><strong>Jurisdicción:</strong> {case.jurisdiction}</li>"
            f"<li><strong>Urgencia:</strong> {case.urgency}</li>"
            f"</ul>"
        )
    else:
        subject = f"Creación de caso #{case.id}"
        body = f"<p>Se ha creado el caso #{case.id} en humanlaw.</p>"
    
    # Si se requiere limitar el mensaje a cierta cantidad de caracteres, se puede hacer un corte, aunque se recomienda
    # mantener el cuerpo completo en HTML para mensajes de correo.
    return subject, body
