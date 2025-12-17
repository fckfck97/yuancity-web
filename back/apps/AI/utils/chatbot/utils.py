import re
import json
from apps.AI.models import ChatMessage
from .memory import get_history
# -------------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------------
def create_ai_message(text: str) -> ChatMessage:
    return ChatMessage.objects.create(user=None, text=text, is_ai=True)

def format_response(text: str) -> str:
    lines = text.split('\n')
    unique_lines = []
    seen = set()
    for line in lines:
        clean_line = re.sub(r'\W+', '', line).lower()
        if clean_line not in seen:
            unique_lines.append(line)
            seen.add(clean_line)
    return "\n".join(unique_lines)

def extract_json(text: str) -> dict:
    # Intenta extraer JSON de bloques de código o del texto
    code_blocks = re.findall(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    if code_blocks:
        try:
            return json.loads(code_blocks[0])
        except json.JSONDecodeError:
            pass
    json_match = re.search(r'{.*}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError("No se encontró JSON válido en la respuesta")


def send_ai_response(session_id: str, message: str) -> dict:
    """
    Envía un mensaje de la IA (por ejemplo un 'mensaje inicial').
    """
    # 1) Crea el mensaje en la BD
    ai_message = ChatMessage.objects.create(
        user=None,
        text=message,
        is_ai=True
    )

    # 2) Lo agrega a la memoria
    history_obj = get_history(session_id)
    history_obj.add_db_message(ai_message)

    # 3) Retorna el dict
    return {"ai_response": {"id": ai_message.id, "text": message}}
