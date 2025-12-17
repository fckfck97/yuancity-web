# memory.py
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from apps.AI.models import ChatMessage

session_memories = {}

class CustomChatHistory(InMemoryChatMessageHistory):
    """
    Almacena internamente HumanMessage o AIMessage en self.messages,
    de modo que podamos acceder a .content directamente.
    """
    def add_db_message(self, chat_message: ChatMessage):
        if chat_message.is_ai:
            # Crear un AIMessage con el texto del ChatMessage
            new_msg = AIMessage(content=chat_message.text)
        else:
            # Crear un HumanMessage con el texto del ChatMessage
            new_msg = HumanMessage(content=chat_message.text)
        
        self.messages.append(new_msg)

def get_history(session_id: str) -> CustomChatHistory:
    if session_id not in session_memories:
        session_memories[session_id] = CustomChatHistory(session_id=session_id)
    return session_memories[session_id]
