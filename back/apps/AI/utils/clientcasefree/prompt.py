# free_case_chain.py
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# Inicializa el modelo de chat (ajusta el nombre del modelo y proveedor según tus necesidades)
llm = init_chat_model("o3-mini-2025-01-31", model_provider="openai")

# Cadena para respuesta general
legal_assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Eres un abogado virtual de HumanLaw. Responde preguntas legales de forma profesional y amable cortas y precisas no muy extensas."),
    ("human", "{text}")]
)
legal_assistant_chain = legal_assistant_prompt | llm


def classify_legal_area(description: str) -> str:
    """
    Uses the legal_assistant_chain to identify whether the case description
    belongs to: 'Derecho Penal', 'Derecho Laboral', 'Derecho Civil', 
    or 'Derecho Comercial'.

    Returns a string with the best guess area.
    """
    # Prompt for the model:
    prompt = (
        f"La descripción del caso es: {description}. "
        "Analiza la descripción y responde con una sola de estas áreas: "
        "Derecho Penal, Derecho Laboral, Derecho Civil, Derecho Comercial. "
        "Indica cuál es la más adecuada solo el area responde ."
    )
    
    # Run the chain
    raw_response = legal_assistant_chain.invoke({"text": prompt})
    
    # You could parse it or do some simple checking. For simplicity,
    # let's just return the chain’s raw response:
    print(f"Raw response: {raw_response}")
    return raw_response.content.strip()