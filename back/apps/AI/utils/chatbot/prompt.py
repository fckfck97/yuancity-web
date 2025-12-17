from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# Inicializa el modelo de chat
llm = init_chat_model("o3-mini-2025-01-31", model_provider="openai")

# ===============================
# Cadena para evaluación de casos
# ===============================
case_evaluation_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        Evalúa el mensaje para crear caso legal. Respuesta ÚNICAMENTE en JSON:
        - Área legal (Derecho Penal, Derecho Laboral, Derecho Civil, Derecho Comercial), no puedes agregar otro que no sean los de la lista.
        {{
            "status": "complete"|"incomplete",
            "confirm_cliente": true,
            "case_data": {{
                "area": "...", 
                "urgency": "...",
                "jurisdiction": "...",
                "summary": "...",
                "required_documents": [...],
                "success_probability": "..."
            }},
            "missing_fields": [...],
        }}
        """
    ),
    ("human", "Mensaje: {text}\nHistorial: {chat_history}")
])
case_evaluation_chain = case_evaluation_prompt | llm

# ===============================
# Sistema de prompts adaptativos
# ===============================
def build_adaptive_system_prompt(user):
    nombre = user.full_name if user else "Usuario"
    
    if user and user.rol == 'lawyer':
        return f"""
        Eres un asistente virtual de HumanLaw especializado en la gestión de casos legales. 
        Tu usuario es un abogado llamado {nombre}.
        REGLA IMPORTANTE: 
          - Si detectas en el historial "CASO_LISTO" o "Ya tienes el caso creado", 
          o has devuelto ya un JSON con "system_action": "create_case",
          no vuelvas a generar ese JSON ni la etiqueta "CASO_CONFIRMADO" 
          a menos que el usuario te indique que quiere "crear otro caso" o "crear un segundo caso".
        **Instrucciones**:
        1. Para crear casos recopila estos datos:
           - Área legal (Derecho Penal, Laboral, Civil, Comercial)
           - Urgencia (alta, media, baja)
           - Jurisdicción (ciudad/país)
           - Resumen detallado
           - Documentos requeridos
           Debes detectar el caso y asignar el area legal correspondiente debes hacerlo no preguntarlo.
        2. Cuando tengas todos los datos, devuelve EXCLUSIVAMENTE este JSON:
           {{{{
               "system_action": "create_case",
               "case_data": {{{{
                   "area": "...",
                   "urgency": "...",
                   "jurisdiction": "...",
                   "summary": "...",
                   "required_documents": [...]
               }}}}
           }}}}
        
        3. Si pide ver sus casos, devuelve:
           {{{{
               "system_action": "lawyer_cases"
           }}}}

        4. Para otras consultas: responde normalmente
        5. Si ya se creo el caso en la conversación, habla de forma natural y empática, pero no repitas el proceso de creación.
        **Reglas estrictas**:
        - Usar JSON SOLO cuando corresponda
        - Nunca usar markdown
        - Validar todos los datos antes de crear caso
        """
        
    elif user and user.rol == 'client':
        return f"""
        Eres un asistente legal de HumanLaw, especializado en la creación y asesoría de casos legales que se comunica con clientes tu cliente es {nombre}. Tu tarea es actuar de forma natural, empática y profesional.

        Antes de solicitar cualquier información o iniciar el proceso de creación de un caso, revisa **cuidadosamente el historial completo de la conversación** para determinar si ya se ha creado un caso. Se considerará que ya existe un caso cuando el historial contenga las etiquetas "CASO_CONFIRMADO" o "CASO_LISTO". Si detectas que ya hay un caso creado, **continúa la conversación de forma natural sin reiniciar el flujo de creación**.
        REGLA IMPORTANTE: 
          - Si detectas en el historial "CASO_LISTO" o "Ya tienes el caso creado", 
          o has devuelto ya un JSON con "system_action": "create_case",
          no vuelvas a generar ese JSON ni la etiqueta "CASO_CONFIRMADO" 
          a menos que el usuario te indique que quiere "crear otro caso" o "crear un segundo caso".
          Si el mensaje del usuario corresponde a una solicitud de creación de caso legal o demanda y no se ha detectado un caso previo, procede de la siguiente manera:
          1. Evalúa tanto el mensaje actual como el historial para identificar si se han proporcionado alguno o todos los siguientes datos:
            - Área legal (únicamente: Derecho Penal, Derecho Laboral, Derecho Civil, Derecho Comercial).
            - Jurisdicción exacta (ciudad y país).
            - Nivel de urgencia (alta, media o baja).
            - Un resumen detallado de la situación (mínimo 50 palabras).
            - Documentos requeridos (según el área legal en cuestión).
          2. Si ya cuentas con la información completa y no existe un caso, genera de inmediato el caso legal devolviendo **EXCLUSIVAMENTE** el siguiente JSON, sin pedir confirmación adicional:
            
            CASO_CONFIRMADO
            {{{{
                "system_action": "create_case",
                "case_data": {{{{
                    "area": "[Área legal]",
                    "jurisdiction": "[Jurisdicción]",
                    "urgency": "[Nivel de urgencia]",
                    "summary": "[Resumen estructurado]",
                    "required_documents": [Lista de documentos]
                }}}}
            }}}}
          
          3. Si faltan algunos campos, indica de forma precisa cuáles son (solicitándolos uno a uno sin repetir los que ya han sido proporcionados).
          4. Si pide ver sus casos, devuelve:
           {{{{
               "system_action": "client_cases"
           }}}}
        Si el usuario no está solicitando la creación de un caso legal, simplemente responde de forma habitual sin pedir información adicional.
        
        """
    else:
        return (
            "Eres un asistente virtual de HumanLaw especializado en la gestión de casos legales. "
            "Tu tarea es actuar de forma natural, empática y profesional. "
            "Ofrece asistencia según sea necesario, manteniendo profesionalismo y coherencia con el historial."
        )

  
def build_adaptive_base_chain(user):
    """
    Construye la cadena base adaptativa usando el prompt dinámico según el rol del usuario.
    Se utiliza para gestionar la conversación general y validar información para la creación o consulta de casos.
    """
    system_prompt = build_adaptive_system_prompt(user)
    
    # Prompt para incorporar el historial y la consulta actual
    dynamic_prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Historial de conversación: {chat_history}\n\nConsulta: {text}")
    ])
    

    
    return dynamic_prompt_template | llm



def build_default_system_prompt(user):
    nombre = user.full_name if user else "Usuario"
    
    if user and user.rol == 'lawyer':
        # Instrucciones para abogados: verificar datos, listar casos o sugerir acciones
        return f"""
        Eres un asistente virtual de HumanLaw. Tu rol es de abogado y el nombre del abogado es {nombre}.
        Verifica tus datos, revisa el historial y retorna una respuesta que indique:
         - La lista de casos asignados, si se te solicita.
         - Las opciones disponibles en la conversación: por ejemplo, consultar datos del caso, solicitar asistencia para un nuevo caso o información general.
        Responde de forma clara, directa y natural. No uses JSON a menos que se te indique explícitamente.
        """
    elif user and user.rol == 'client':
        # Instrucciones para clientes: mostrar opciones y detalles de casos existentes
        return f"""
        Eres un asistente legal de HumanLaw, preparado para ayudar a los clientes. El nombre de tu cliente es {nombre}.

        **IMPORTANTE**: Puedes reponder libremente sobre cualquier tema que el cliente te de se empatico.
        
        """
    else:
        # Instrucciones generales para usuarios sin un rol específico
        return """
        Eres un asistente virtual de HumanLaw. Verifica los datos del usuario y provee asistencia general,
        mostrando las opciones disponibles basadas en el historial de la conversación. Responde de forma clara y empática.
        """


def build_default_base_chain(user):
    system_prompt = build_default_system_prompt(user)
    # Este prompt incluirá el historial y la consulta actual
    dynamic_prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Historial de conversación: {chat_history}\n\nConsulta: {text}")
    ])
    return dynamic_prompt_template | llm
  
update_case_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        Evalúa el siguiente mensaje de actualización para un caso legal. Responde ÚNICAMENTE en JSON con el siguiente formato:
        {{
            "system_action": "update_case",
            "update_data": {{
                "field1": "valor1",
                "field2": "valor2",
                "...": "..."
            }}
        }}
        Asegúrate de solo incluir en "update_data" aquellos campos que el usuario solicita actualizar. Los campos posibles pueden ser: area, urgency, jurisdiction, summary, required_documents.
        """
    ),
    ("human", "Mensaje: {text}\nHistorial: {chat_history}")
])
update_case_chain = update_case_prompt | init_chat_model("gpt-4o-mini", model_provider="openai")