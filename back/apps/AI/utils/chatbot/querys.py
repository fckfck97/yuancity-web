from apps.AI.models import Case
from apps.user.models import UserAccount as User
from apps.user.models import LawyerProfile
from typing import Any
# -------------------------------------------------------------------
# Asignación y Consulta para Abogados y Clientes
# -------------------------------------------------------------------
def assign_lawyer(case: Case, user: None) -> Any:
    if user.rol == 'lawyer':
        profile = LawyerProfile.objects.filter(
            user=user,
            specialties__icontains=case.area,
            is_available=True
        ).first()
        # Si NO te interesa comparar current_caseload < max_caseload,
        # elimina la validación y usa directamente el perfil si existe:
        if profile:
            profile.current_caseload += 1
            profile.save()
            return user
    
    available_profile = LawyerProfile.objects.filter(
        specialties__icontains=case.area,
        is_available=True
    ).order_by('current_caseload').first()
    
    if available_profile:
        available_profile.current_caseload += 1
        available_profile.save()
        return available_profile.user

    return None


def get_lawyer_cases(user: User) -> dict:
    """
    Devuelve los casos asignados al abogado con detalles en formato Markdown.
    """
    cases = Case.objects.filter(assigned_lawyer=user).order_by('-created_at')
    if not cases.exists():
        return "📭 No tienes casos asignados actualmente. ¿Te puedo ayudar en algo más?"
    
    response_lines = ["**📂 Tus casos asignados:**", ""]
    for case in cases:
        status_icon = "🟢" if case.status == "asignado" else "⚪"
        case_details = (
            f"**{status_icon} Caso #{case.id}**\n\n"
            f"- **Área:** {case.area}\n"
            f"- **Urgencia:** {case.urgency}\n"
            f"- **Jurisdicción:** {case.jurisdiction}\n"
            f"- **Resumen:** {case.summary}\n"
            f"- **Documentos requeridos:** {', '.join(case.required_documents)}\n"
        )
        response_lines.append(case_details)
    
    formatted_response = "\n\n---\n\n".join(response_lines)
    
    return formatted_response


def get_client_case(user: User) -> str:
    """
    Busca el caso del cliente y devuelve un mensaje formateado en Markdown con sus detalles.
    """
    client_case = Case.objects.filter(client=user).order_by('-created_at').first()
    if client_case:
        abogado = client_case.assigned_lawyer.get_full_name() if client_case.assigned_lawyer else 'No asignado'
        # Formatea los documentos en una lista Markdown.
        documentos = "\n".join([f"- {doc}" for doc in client_case.required_documents])
        return (
            f"**CASO EXISTE ✅**\n\n"
            f"---\n\n"
            f"**Caso:** #{client_case.id}\n\n"
            f"**Área:** {client_case.area}\n\n"
            f"**Urgencia:** {client_case.urgency}\n\n"
            f"**Jurisdicción:** {client_case.jurisdiction}\n\n"
            f"**Resumen:**\n\n"
            f"{client_case.summary}\n\n"
            f"**Documentos requeridos:**\n\n"
            f"{documentos}\n\n"
            f"**Abogado asignado:** {abogado}\n\n"
            f"---"
        )
    else:
        return "📭 No tienes casos creados actualmente."

