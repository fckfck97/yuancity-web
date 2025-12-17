from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain_community.document_loaders.parsers import TesseractBlobParser
import os

def load_pdf_document(file_path, mode="page"):
    """
    Carga un PDF usando PyPDFLoader.
    
    mode:
      - "page": divide el PDF en páginas (cada página es un documento)
      - "single": extrae todo el PDF como un único documento (con opción de delimitar páginas)
    """
    loader = PyPDFLoader(file_path, mode=mode)
    docs = loader.load()
    
    return docs

def load_image_document(file_path):
    """
    Carga una imagen usando UnstructuredImageLoader y TesseractBlobParser.
    """
    loader = UnstructuredImageLoader(file_path, mode="elements", strategy="fast",)
    docs = loader.load()
    return docs

