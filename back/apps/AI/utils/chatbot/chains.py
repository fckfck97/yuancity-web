# chain.py
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.runnables.history import RunnableWithMessageHistory

# Importaciones de tu proyecto
from apps.AI.models import Case
from apps.user.models import UserAccount as User
from .prompt import build_adaptive_base_chain, case_evaluation_chain
from .utils import format_response, extract_json, create_ai_message, send_ai_response
from .memory import get_history
from .querys import get_lawyer_cases, get_client_case
from .case import process_case_creation
from .session import get_session_data, save_session_data, delete_session_data
from typing import Any

# -------------------------------------------------------------------
# 2) Router que determina la acción ("system_action") en JSON
# -------------------------------------------------------------------
def invoke_router(chat_history: str, text: str, user_role: str) -> dict:
    """
    Invoca el prompt de enrutamiento para determinar la acción a tomar según
    el historial y la consulta.
    Devuelve un dict con 'system_action'.
    """
    router_prompt_template = PromptTemplate(
    input_variables=["chat_history", "text", "user_role"],
    template="""
      Analiza el siguiente historial, la consulta del usuario y su rol para decidir qué acción tomar.
      Si el usuario es abogado y la consulta es para ver casos, responde EXACTAMENTE en JSON:
        {{"system_action": "lawyer_cases"}}
      Si el usuario es cliente y la consulta es para ver casos, responde en JSON:
        {{"system_action": "client_cases"}}
      Si la consulta es para crear un caso legal, responde EXACTAMENTE en JSON:
        {{"system_action": "create_case"}}
      Si ninguna acción especial es necesaria, responde con:
        {{"system_action": "default"}}

      Rol del usuario: {user_role}
      Historial: {chat_history}
      Consulta: {text}
    """
    )
    llm_router = init_chat_model("gpt-4o-mini", model_provider="openai")
    formatted_prompt = router_prompt_template.format(
        chat_history=chat_history, text=text, user_role=user_role
    )

    # Se invoca el modelo y se obtiene el texto
    router_response = llm_router.invoke(formatted_prompt)
    router_response_str = (
        router_response if isinstance(router_response, str)
        else router_response.content
    )

    # Extraemos JSON ({"system_action": "..."}); puede lanzar excepción si no es válido
    return extract_json(router_response_str)

# -------------------------------------------------------------------
# 3) Funciones de manejo de cada "system_action"
# -------------------------------------------------------------------
def handle_case_creation(session_id: str, text: str, user: User, response_text: str) -> dict:
    """
    Llamada cuando el router dice 'create_case'.
    Internamente invoca la 'case_evaluation_chain' y crea el caso si está listo.
    """
    try:
        # Confirmamos que la respuesta del LLM tenga "system_action": "create_case"
        json_data = extract_json(response_text if isinstance(response_text, str) else response_text.content)
        if json_data.get("system_action") == "create_case":
            history_obj = get_history(session_id)
            recent_history = "\n".join([msg.content for msg in history_obj.messages[-4:]])

            evaluation = case_evaluation_chain.invoke({
                "text": text,
                "chat_history": recent_history
            })
            return process_case_creation(evaluation.content, text, user)
        
        # Si no trae "system_action" = "create_case", devolvemos la respuesta tal cual
        return send_ai_response(session_id,response_text if isinstance(response_text, str) else response_text.content)
    except Exception as e:
        return {"ai_response": {"text": f"⚠️ Error en creación de caso: {str(e)}"}}

def route_action(session_id: str, text: str, user: User, response_text: str) -> dict:
    """
    Función genérica que, dado 'response_text', extrae 'system_action' y redirige 
    a la función apropiada (crear caso, ver casos, etc.).
    """
    try:
        json_data = extract_json(response_text if isinstance(response_text, str) else response_text.content)
        system_action = json_data.get("system_action", None)

        if system_action == "create_case":
            return handle_case_creation(session_id, text, user, response_text)
        elif system_action == "client_cases":
            client_case = get_client_case(user)
            if client_case:
                return send_ai_response(session_id, client_case)
        elif system_action == "lawyer_cases":
            lawyer_cases = get_lawyer_cases(user)
            if lawyer_cases:
                return send_ai_response(session_id, lawyer_cases)
        else:
            # Devuelve la respuesta tal cual sin acción especial
            return send_ai_response(session_id, response_text if isinstance(response_text, str) else response_text.content)
    except Exception as e:
        # Si falla extrayendo JSON, retornamos la respuesta textual original
        print(f"Error en el enrutamiento: {str(e)}")
        return send_ai_response(session_id, response_text if isinstance(response_text, str) else response_text.content)
# -------------------------------------------------------------------
# 4) Flujo de creación de caso (cuando se está en modo 'in_case_creation')
# -------------------------------------------------------------------
def continue_case_creation_flow(session_id: str, text: str, user: User) -> dict:
    """
    Maneja la recopilación de datos para crear un caso SÓLO si in_case_creation=True.
    Verifica si la evaluación está completa. Si no, pide los datos faltantes.
    """
    session_data = get_session_data(session_id)
    history_obj = get_history(session_id)

    # 1) Invoca la cadena de evaluación para ver si tenemos datos completos
    recent_history = "\n".join([msg.content for msg in history_obj.messages[-4:]]) if history_obj else ""
    evaluation = case_evaluation_chain.invoke({
        "text": text,
        "chat_history": recent_history
    })

    try:
        eval_json = extract_json(evaluation.content)
    except Exception as e:
        return {"ai_response": {"text": f"Error al analizar la información del caso: {str(e)}"}}

    status = eval_json.get("status", "incomplete")
    if status == "complete":
        # 2) Ya tenemos toda la info. Creamos el caso:
        response = process_case_creation(evaluation.content, text, user)
        # 3) Salimos del modo creación y guardamos
        session_data["in_case_creation"] = False
        save_session_data(session_id, session_data)
        return response
    else:
        # 4) Falta información. Solicitamos campos faltantes
        missing_fields = eval_json.get("missing_fields", [])
        formatted_fields = "\n- ".join(missing_fields)
        missing_info_prompt = PromptTemplate(
            input_variables=["formatted_fields"],
            template="""
          **Falta Información para Crear el Caso**
          Para crear tu caso legal, todavía necesitamos la siguiente información adicional:
          - {formatted_fields}

          Por favor, proporciona los datos que faltan.
          """
        )
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        dynamic_prompt = missing_info_prompt.format(formatted_fields=formatted_fields)
        ai_response = llm.invoke(dynamic_prompt)
        return {"ai_response": {"text": ai_response.content}}

# -------------------------------------------------------------------
# 5) Flujo principal: process_normal_message
# -------------------------------------------------------------------
def process_normal_message(session_id: str, text: str, user: User) -> dict:
    """
    Procesa un mensaje del usuario revisando el estado de la sesión.
    1) Si in_case_creation=True, continúa la creación de caso.
    2) Si user no existe, usa un prompt genérico sin enrutamiento.
    3) Si no, usa el enrutamiento (router) para ver qué hacer (crear/ver casos/normal).
    """
    # ----------------------------------------------------------------
    # A) Validación de usuario: si es None o no tiene 'id', genérico:
    # ----------------------------------------------------------------

    if user is None or not getattr(user, "id", None):
        return run_generic_conversation(session_id, text)

    # ----------------------------------------------------------------
    # B) Si usuario válido, revisamos el estado de sesión
    # ----------------------------------------------------------------
    session_data = get_session_data(session_id)
    history_obj = get_history(session_id)
    chat_history = (
        "\n".join([msg.content for msg in history_obj.messages[-4:]])
        if history_obj and history_obj.messages else ""
    )

    # ----------------------------------------------------------------
    # C) Si estamos en creación de caso, continuar ese flujo
    # ----------------------------------------------------------------
    if session_data.get("in_case_creation", False):
        return continue_case_creation_flow(session_id, text, user)

    # ----------------------------------------------------------------
    # D) De lo contrario, invocamos el router
    # ----------------------------------------------------------------
    rol = user.rol if user and getattr(user, "rol", None) else "unknown"
    router_result = invoke_router(chat_history, text, rol)
    system_action = router_result.get("system_action", "default")

    # ----------------------------------------------------------------
    # E) Manejo de system_action del router
    # ----------------------------------------------------------------
    if system_action == "create_case":
        # Entramos en modo creación de caso
        session_data["in_case_creation"] = True
        save_session_data(session_id, session_data)

        # Mensaje inicial pidiendo datos
        markdown_msg = (
            "**Entendido. Iniciemos la creación de tu caso legal.**\n\n"
            "Por favor, proporciona la siguiente información para continuar:\n\n"
            "- **Área legal:** (ej. Derecho Penal, Laboral, Civil, Comercial)\n"
            "- **Nivel de urgencia:** (alta, media o baja)\n"
            "- **Jurisdicción:** (ciudad y país)\n"
            "- **Resumen del caso:** (descripción detallada del caso, mínimo 50 palabras)\n"
            "- **Documentos requeridos:** (lista de documentos necesarios según el área legal)\n\n"
            "Si necesitas ayuda adicional, no dudes en preguntar."
        )
        return send_ai_response(session_id,markdown_msg)

    elif system_action == "client_cases":
        client_case = get_client_case(user)
        if client_case:
            return send_ai_response(session_id, client_case)

    elif system_action == "lawyer_cases":
        lawyer_cases = get_lawyer_cases(user)
        if lawyer_cases:
            return send_ai_response(session_id, lawyer_cases)

    else:
        # Conversación normal
        return run_adaptive_conversation(session_id, text, user)

# -------------------------------------------------------------------
# 6) Funciones auxiliares de conversación
# -------------------------------------------------------------------
def run_generic_conversation(session_id: str, text: str) -> dict:
    """
    Si no hay usuario o no es válido, usamos un prompt genérico.
    """
    chain_with_history = RunnableWithMessageHistory(
        build_adaptive_base_chain(None),
        get_session_history=lambda sid: get_history(session_id),
        input_messages_key="text",
        history_messages_key="chat_history"
    )
    response = chain_with_history.invoke(
        {"text": text},
        config={"configurable": {"session_id": session_id}}
    )
    response_text = response.content
    formatted_response = format_response(response_text)
    ai_message = create_ai_message(formatted_response)
    return {"ai_response": {"id": ai_message.id, "text": formatted_response}}

def run_adaptive_conversation(session_id: str, text: str, user: User) -> dict:
    """
    Conversación normal cuando sí hay un usuario válido y no se ha disparado ninguna acción especial.
    """
    chain_with_history = RunnableWithMessageHistory(
        build_adaptive_base_chain(user),
        get_session_history=lambda sid: get_history(session_id),
        input_messages_key="text",
        history_messages_key="chat_history"
    )
    response = chain_with_history.invoke(
        {"text": text},
        config={"configurable": {"session_id": session_id}}
    )
    response_text = response.content
    formatted_response = format_response(response_text)
    ai_message = create_ai_message(formatted_response)
    return {"ai_response": {"id": ai_message.id, "text": formatted_response}}

