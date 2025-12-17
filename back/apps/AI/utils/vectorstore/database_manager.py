from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from langchain_pinecone import PineconeVectorStore

class DatabaseManager:

    def __init__(self, documents, persist_directory):
        self.documents = documents
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()
        self.chunk_size = 1500
        self.chunk_overlap = 150
        self.add_start_index = True
        self.index_name = "humanlaw"

    def preprocess_documents(self, docs):
        for doc in docs:
            if 'content' in doc:
                doc['content'] = doc['content'].lower()
        return docs

    def split_documents(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            add_start_index=self.add_start_index,
        )
        return text_splitter.split_documents(docs)

    def create_database(self, docs_split):
        # Pinecone
        return PineconeVectorStore.from_documents(docs_split, self.embedding, index_name=self.index_name)
        
        # Local
        # return Chroma.from_documents(
        #     documents=docs_split,
        #     embedding=self.embedding,
        #     persist_directory=self.persist_directory,
        # )

    def initialize(self):
        preprocessed_docs = self.preprocess_documents(self.documents)
        docs_split = self.split_documents(preprocessed_docs)
        return self.create_database(docs_split)
      
    @classmethod
    def get_retriever(cls, collection_name: str = None):
        """Conecta a Pinecone y devuelve un retriever del vector store existente"""
        # Configura embeddings y conexión a Pinecone
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("APIKEY"))
        pc = PineconeVectorStore(api_key=os.getenv("PINECODE"))
        
        # Usa el índice configurado en la clase
        index = pc.Index(cls.index_name)
        
        # Crea el vector store conectado al índice existente
        vector_store = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key=cls.text_field
        )
        
        return vector_store.as_retriever()