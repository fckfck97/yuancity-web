from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# Inicializa el modelo de chat
llm = init_chat_model("o3-mini-2025-01-31", model_provider="openai")

# Prompt especializado para generación de documentos
document_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "Eres un asistente virtual experto en generar documentos legales y técnicos. Sigue estas reglas:\n"
            "1. Siempre genera el documento solicitado después de '--- DOCUMENTO ---'\n"
            "2. Usa placeholders [ENTRE CORCHETES] para información faltante\n"
            "3. El texto antes del delimitador debe ser una confirmación breve (1-2 oraciones) que indique que el documento está listo y, en caso de ser necesario, solicite la información adicional para completar los campos marcados\n"
            "4. Estructura profesional con encabezados y secciones\n"
            "5. En caso de que se requiera más información, incluye un mensaje como: 'Por favor, proporciona los datos necesarios para completar los campos marcados'\n"
            "6. ¡Nunca omitas el delimitador ni incluyas el documento antes de él!\n"
            "7. No incluyas información adicional o instrucciones fuera del delimitador\n"
            "8. Asesora sobre el llenado de los datos del documento siempre que generes un documento\n"
            "9. Verificar y solicitar activar el buscar para mejorar el documento, si se da el caso \n"
            "Ejemplo:\n"
            "Claro, aquí tienes tu contrato base. Revisa los campos marcados y, si necesitas ayuda adicional, indica los datos faltantes.\n"
            "En tu respuesta antes de '--- DOCUMENTO ---', incluye un mensaje como: 'Por favor, proporciona los datos necesarios para completar los campos marcados y bonito en markdown los campos que se necesitan llenar'.\n"
            "--- DOCUMENTO ---\n"
            "# CONTRATO DE ARRENDAMIENTO\n\n"
            "Entre [NOMBRE ARRENDADOR] y [NOMBRE ARRENDATARIO]..."
        )
    ),
    (
        "human",
        "Historial: {chat_history}\nSolicitud: {text}"
    )
])
document_chain = document_prompt_template | llm

# Prompt para mejorar documentos
improve_document_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        "COMO EXPERTO JURÍDICO-MARKDOWN:\n"
        "1. Corregir errores sustantivos y formales\n"
        "2. Mantener estructura jerárquica original (##/###)\n"
        "3. Conservar numeración legal intacta\n"
        "4. Aplicar formato Markdown válido\n"
        "5. Respetar hipervínculos y metadatos\n"
        "6. **RESPUESTA ESTRICTA:** ÚNICAMENTE el documento mejorado en Markdown\n"
        "7. **NO:** Responder  **Arrendador:** sino  de esta manera con los : fuera **Arrendador**:, Responder [Jesús Delgado Carrera] sino Jesús Delgado, Responder [Firma del Arrendador] [Firma del Arrendatario] sino los nombres del arrendatario y arrendador bonito\n"
        "8. **PROHIBIDO:** Comentarios, explicaciones o texto adicionales como por ejemplo 'Por favor, proporciona los datos necesarios para completar los campos marcados.'\n"
    ),
    (
        "human",
        "DOCUMENTO ORIGINAL (Markdown):\n"
        "{doc_response}\n\n"
        "REGLAS ABSOLUTAS:\n"
        "- NO uses ```markdown\n"
        "- NO agregues encabezados ni pies\n"
        "- NO incluyas 'Documento mejorado' ni títulos extras\n"
        "- SOLO el contenido válido entrega"
    )
])
improve_document_chain = improve_document_prompt_template | llm