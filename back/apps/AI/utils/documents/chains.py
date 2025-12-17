from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from apps.AI.models import ChatMessage
from .prompt import document_chain,improve_document_chain
from apps.user.models import UserAccount as User
from langchain.chat_models import init_chat_model
# Mantenemos session_memories para conservar historial de mensajes en memoria
session_memories = {}
class CustomChatHistory(InMemoryChatMessageHistory):
    def add_message(self, message: ChatMessage):
        if message.type in ['human', 'assistant']:
            super().add_message(message)

def get_history(session_id: str) -> CustomChatHistory:
    if session_id not in session_memories:
        session_memories[session_id] = CustomChatHistory(session_id=session_id)
    return session_memories[session_id]


def create_ai_message(text: str) -> ChatMessage:
    """Crea y guarda un mensaje de respuesta de IA."""
    return ChatMessage.objects.create(
        user=None,
        text=text,
        is_ai=True
    )

def process_document_message(session_id: str, text: str) -> dict:
    """
    Procesa solicitud para generar documentos legales/técnicos con la cadena 'document_chain'.
    (Sin cambio, se mantiene como tu ejemplo actual).
    """
    chain_with_history = RunnableWithMessageHistory(
        document_chain,
        get_session_history=lambda sid: get_history(session_id),
        input_messages_key="text",
        history_messages_key="chat_history"
    )
    response = chain_with_history.invoke(
        {"text": text},
        config={"configurable": {"session_id": session_id}}
    )
    content = response.content
    # Separa la respuesta en confirmación y contenido del documento
    parts = content.split('--- DOCUMENTO ---')
    ai_response_text = parts[0].strip()
    doc_content = parts[1].strip() if len(parts) > 1 else ""

    ai_message = create_ai_message(ai_response_text)

    if doc_content:
        try:
            improved_response = improve_document_chain.invoke({"doc_response": doc_content})
            improved_doc_content = improved_response.content
        except Exception:
            improved_doc_content = doc_content
        doc_message = create_ai_message(improved_doc_content)
    else:
        doc_message = None

    return {
        "ai_response": {"id": ai_message.id, "text": ai_message.text},
        "doc_response": {"id": doc_message.id, "text": doc_message.text} if doc_message else {"id": None, "text": ""}
    }
