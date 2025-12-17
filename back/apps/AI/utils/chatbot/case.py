from .notifications import send_sms_in_background,send_email_in_background, create_case_creation_email
from .querys import assign_lawyer 
from apps.AI.models import Case
from apps.user.models import UserAccount as User
from .utils import format_response, extract_json, create_ai_message

def create_case_from_data(case_data: dict, user: User) -> Case:
    """
    Crea un caso utilizando todos los campos extraídos de la evaluación.
    Se incluyen: área, urgencia, jurisdicción, resumen, documentos requeridos y
    la probabilidad de éxito (si está presente).
    """
    return Case.objects.create(
        client=user if user.rol == 'client' else None,
        area=case_data.get("area", ""),
        urgency=case_data.get("urgency", ""),
        jurisdiction=case_data.get("jurisdiction", ""),
        summary=case_data.get("summary", ""),
        required_documents=case_data.get("required_documents", []),
        status='nuevo'
    )

def create_sms_message(user: User, case: Case) -> str:
    """
    Genera el mensaje SMS en función del rol del usuario y limita el mensaje a 160 caracteres.
    """
    if user.rol == "client":
        message = (
            f"Felicidades {user.full_name}, hemos tomado tu caso en humanlaw. "
            "El abogado encargado se comunicará contigo pronto."
        )
    elif user.rol == "lawyer":
        message = (
            f"{user.full_name}, se ha creado tu caso en humanlaw.ai: #{case.id}."
        )
    else:
        message = f"Se ha creado el caso #{case.id} en humanlaw."
    return message[:160]

def process_case_creation(response_text: str, original_text: str, user: User) -> dict:
  """
  Devuelve la respuesta estructurada de manera consistente.
  Crea el caso, asigna un abogado, envía notificaciones por SMS y correo electrónico.
  """
  try:
    json_data = extract_json(response_text)
    if json_data.get("status") == "complete":
      case_data = json_data.get("case_data", {})
      new_case = create_case_from_data(case_data, user)
      assigned_lawyer = assign_lawyer(new_case, user)
      new_case.assigned_lawyer = assigned_lawyer
      new_case.status = 'asignado'
      new_case.save()

      response_content = (
        f"**CASO_LISTO ✅**\n\n"
        f"**Caso:** #{new_case.id} creado\n\n"
        f"- **Área:** {new_case.area}\n"
        f"- **Urgencia:** {new_case.urgency}\n"
        f"- **Jurisdicción:** {new_case.jurisdiction}\n"
        f"- **Resumen:**\n{new_case.summary}\n\n"
        f"- **Documentos requeridos:** {', '.join(new_case.required_documents)}\n"
        f"- **Abogado asignado:** {assigned_lawyer.full_name if assigned_lawyer else 'No asignado'}\n\n"
        "Ya tienes el caso creado."
      )

      # Notificación SMS
      if user.phone:
        sms_text = create_sms_message(user, new_case)
        send_sms_in_background(
          to_number=user.phone,
          body_text=sms_text,
        )
      
      # Notificación por correo electrónico (si el usuario tiene email configurado)
      if user.email:
        email_subject, email_body = create_case_creation_email(user, new_case)
        send_email_in_background(email_subject, email_body, user.email)
      
      formatted_response = format_response(response_content)
      ai_message = create_ai_message(formatted_response)

      return {
        "ai_response": {
          "id": ai_message.id,
          "text": formatted_response
        }
      }

    return {"ai_response": {"text": json_data.get("message", response_text)}}
  except Exception as e:
    error_msg = f"⚠️ Error: {str(e)}"
    return {"ai_response": {"text": error_msg}}
