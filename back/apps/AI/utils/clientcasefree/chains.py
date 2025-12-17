from .prompt import legal_assistant_chain
from .memory import get_history, create_ai_message, format_response
from langchain_core.runnables.history import RunnableWithMessageHistory

def process_case_free(session_id: str, text: str) -> dict:

    """
    Procesa el caso gratuito y devuelve la respuesta generada por el modelo.
    """
    history_obj = get_history(session_id)
    
    # Genera la respuesta utilizando la cadena de asistente legal
    chain_with_history = RunnableWithMessageHistory(
      legal_assistant_chain,
      get_session_history=lambda sid: get_history(session_id),
      input_message_key="text",
      history_message_key="chat_history")
    response = chain_with_history.invoke(
        {"text": text},
        config={"configurable": {"session_id": session_id}}
    )
    
    response_text = response.content
    formatted_response = format_response(response_text)
    ai_message = create_ai_message(formatted_response)
    return {"ai_response": {"id": ai_message.id, "text": formatted_response}}