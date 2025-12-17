from typing import Dict

# Diccionario global para ejemplo. En producción podrías usar DB o Redis
SESSIONS_DATA: Dict[str, Dict] = {}

def get_session_data(session_id: str) -> dict:
    """
    Retorna el estado de la sesión. Si no existe, inicializa un dict vacío.
    """
    return SESSIONS_DATA.setdefault(session_id, {})

def save_session_data(session_id: str, data: dict) -> None:
    """
    Guarda (o actualiza) el estado de sesión en nuestro diccionario.
    """
    SESSIONS_DATA[session_id] = data

def delete_session_data(session_id: str) -> None:
    """
    Elimina el estado de la sesión (para reiniciar la conversación o limpiar).
    """
    if session_id in SESSIONS_DATA:
        del SESSIONS_DATA[session_id]

