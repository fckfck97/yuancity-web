from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ChatMessage, ClientCase
from langchain_community.tools import DuckDuckGoSearchRun
import os
import threading
# Importaciones de loaders y otros módulos
from .utils.loaders.pdfloader import load_pdf_document, load_image_document
from .utils.loaders.wordloader import load_word_document
from .utils.loaders.excelloader import load_excel_document
from .utils.chatbot.chains import process_normal_message
from .utils.documents.chains import process_document_message

from .utils.vectorstore.database_manager import DatabaseManager
from .utils.vectorstore.document_loader import read_doc

from .utils.clientcasefree.chains import process_case_free


from .serializers import ClientCaseSerializer
class ChatAPIView(APIView):

    def get_permissions(self):
      """
      Asigna permisos en función de ciertos criterios.
      Por ejemplo, se puede verificar un flag en el request o el método HTTP.
      Aquí se permite el acceso a cualquier usuario en POST si se
      especifica un parámetro (por ejemplo, 'allow_anonymous') y se requieren
      permisos de autenticación en el resto de los casos.
      """
      user = getattr(self.request, "user", None)
      if user and user.is_authenticated:
        return [IsAuthenticated()]
      # Validar si el usuario es AnonymousUser
      if user and str(user) == "AnonymousUser":
        print("El usuario es AnonymousUser")
        return [AllowAny()]


    def post(self, request):
        session_id = request.data.get("session_id", "default_session")
        text = request.data.get("text", "").strip()
        attachment = request.FILES.get("attachment", None)
        generate_document = request.data.get("document", "false").lower() == "true"
        print(request.data)
        # Procesar archivo adjunto
        if attachment:
            processed_text = self.process_attachment(attachment)
            text = f"{text}\n\n{processed_text}" if text else processed_text

        if not text:
            return Response({"error": "El mensaje no puede estar vacío"}, status=400)

        # Agregar resultados de búsqueda si se solicita
        if request.data.get("search", "false").lower() == "true":
            text = self.add_search_results(text)

        # Guardar mensaje del usuario
        self.save_message(request, text, attachment, is_ai=False)

        try:
            user = request.user if request.user.is_authenticated else None
            if generate_document:
                result = process_document_message(session_id, text)
            else:
                result = process_normal_message(session_id, text, user)
            
            return Response(result, status=200)
        except Exception as e:
            error_msg = "Error generando la respuesta" if generate_document else "Error en la conversación"
            return Response({"error": f"{error_msg}: {str(e)}"}, status=500)

    def process_attachment(self, attachment):
        # [Implementación de procesamiento de attachment]
        docs = None
        content = "Contenido adjunto no procesado"
        try:
            file_path = os.path.join('/tmp', attachment.name)
            with open(file_path, 'wb+') as f:
                for chunk in attachment.chunks():
                    f.write(chunk)
            file_ext = os.path.splitext(attachment.name)[1].lower()
            doc_type_map = {'.pdf': 'pdf', '.mp4': 'video'}
            doc_type = doc_type_map.get(file_ext, None)
            if doc_type:
                docs = read_doc(doc_type, file_path, metadata=None)
            else:
                loaders = {
                    '.docx': load_word_document,
                    '.xls': load_excel_document,
                    '.xlsx': load_excel_document,
                    '.jpg': load_image_document,
                    '.jpeg': load_image_document,
                    '.png': load_image_document
                }
                loader = loaders.get(file_ext, lambda x: None)
                docs = loader(file_path) if loader else None

            if docs:
                content = "\n".join([doc.page_content for doc in docs if hasattr(doc, 'page_content')])
            else:
                content = "No se pudo procesar el contenido del attachment."

        except Exception as e:
            content = f"Error al procesar el attachment: {e}"
            print(content)

        def process_vector_store():
            try:
                if docs:
                    print("Procesando documentos para el vector store...")
                    db_manager = DatabaseManager(docs, persist_directory="data")
                    preprocessed_docs = db_manager.preprocess_documents(docs)
                    docs_split = db_manager.split_documents(preprocessed_docs)
                    db_manager.create_database(docs_split)
                else:
                    print("No hay documentos para procesar en el vector store.")
            except Exception as e:
                print(f"Error en el procesamiento del vector store: {e}")

        thread = threading.Thread(target=process_vector_store)
        thread.daemon = True
        thread.start()
        return content

    def add_search_results(self, text):
        search_tool = DuckDuckGoSearchRun()
        search_result = search_tool.invoke(text)
        return f"Contexto de búsqueda: {search_result}\n\n{text}"

    def save_message(self, request, text, attachment, is_ai):
        ChatMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            text=text,
            attachment=attachment,
            is_ai=is_ai
        )

class ClientCaseAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = ClientCaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class FreeCaseChatAPIView(APIView):
  permission_classes = [AllowAny]

  def post(self, request):
    session_id = request.data.get("session_id", "default_session")
    text = request.data.get("text", "").strip()
    
    if not text:
      return Response({"error": "El mensaje no puede estar vacío"}, status=400)
    # Guardar mensaje del usuario

    try:
      result = process_case_free(session_id, text)
      return Response(result, status=200)
    except Exception as e:
      return Response({"error": f"Error en la conversación: {str(e)}"}, status=500)