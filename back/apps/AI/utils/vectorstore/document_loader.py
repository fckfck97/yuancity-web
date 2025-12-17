import re
import os
import tempfile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_community.document_loaders import YoutubeAudioLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders import FileSystemBlobLoader
from moviepy import VideoFileClip
import pandas as pd
from docx import Document  # Requiere python-docx

def extract_audio_from_video(video_file, output_audio_path):
    if isinstance(video_file, (InMemoryUploadedFile, TemporaryUploadedFile)):
        temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        with open(temp_video_path, 'wb+') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        video_path = temp_video_path
    else:
        video_path = video_file 
    try:
        clip = VideoFileClip(video_path)
        audio = clip.audio
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        audio.write_audiofile(output_audio_path) 
        audio.close()  
        clip.close()  
    except Exception as e:
        raise IOError(f"Failed to process video file at {video_path}. Error: {str(e)}")
    finally:
        if 'temp_video_path' in locals():
            os.unlink(temp_video_path)
    
def clear_blank_lines(docs):
    for doc in docs:
        doc.page_content = re.sub(r"\n\n\n+", "\n\n", doc.page_content)
    return docs

def read_doc(doc_type, doc_path, metadata=None):
    docs = []
    # Procesar documentos según el tipo
    if doc_type == "pdf":
        if isinstance(doc_path, (InMemoryUploadedFile, TemporaryUploadedFile)):
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            for chunk in doc_path.chunks():
                temp_pdf.write(chunk)
            temp_pdf.close()
            doc_path = temp_pdf.name 
        loader = PyPDFLoader(doc_path)
        docs = loader.load()
    elif doc_type == "url":
        loader = WebBaseLoader(doc_path)
        docs = loader.load()
    elif doc_type == "youtube":
        save_path = "./downloads"
        loader = GenericLoader(
            YoutubeAudioLoader([doc_path], save_path), OpenAIWhisperParser()
        )
        docs = loader.load()
    elif doc_type == "video":
        if isinstance(doc_path, InMemoryUploadedFile):
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            for chunk in doc_path.chunks():
                temp_video.write(chunk)
            temp_video.close()
            doc_path = temp_video.name
        save_path = "./downloads"
        audio_path = os.path.join(save_path, "audio.wav")
        extract_audio_from_video(doc_path, audio_path)
        loader = GenericLoader(
            FileSystemBlobLoader(audio_path), OpenAIWhisperParser()
        )
        docs = loader.load()
    elif doc_type in ["docx", "word"]:
        # Procesar archivos DOCX
        if isinstance(doc_path, (InMemoryUploadedFile, TemporaryUploadedFile)):
            temp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            for chunk in doc_path.chunks():
                temp_doc.write(chunk)
            temp_doc.close()
            doc_path = temp_doc.name
        document = Document(doc_path)
        text = "\n".join([para.text for para in document.paragraphs])
        # Creamos un objeto simple para imitar la estructura de doc
        class SimpleDoc:
            pass
        simple_doc = SimpleDoc()
        simple_doc.page_content = text
        docs = [simple_doc]
        if 'temp_doc' in locals():
            os.unlink(temp_doc.name)
    elif doc_type in ["excel", "xls", "xlsx"]:
        # Procesar archivos Excel
        if isinstance(doc_path, (InMemoryUploadedFile, TemporaryUploadedFile)):
            temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            for chunk in doc_path.chunks():
                temp_excel.write(chunk)
            temp_excel.close()
            doc_path = temp_excel.name
        df = pd.read_excel(doc_path)
        # Convertimos el contenido a CSV (o podrías procesarlo de otra forma)
        text = df.to_csv(index=False)
        class SimpleDoc:
            pass
        simple_doc = SimpleDoc()
        simple_doc.page_content = text
        docs = [simple_doc]
        if 'temp_excel' in locals():
            os.unlink(temp_excel.name)
    elif doc_type == "csv":
        # Procesar archivos CSV
        if isinstance(doc_path, (InMemoryUploadedFile, TemporaryUploadedFile)):
            temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            for chunk in doc_path.chunks():
                temp_csv.write(chunk)
            temp_csv.close()
            doc_path = temp_csv.name
        df = pd.read_csv(doc_path)
        text = df.to_csv(index=False)
        class SimpleDoc:
            pass
        simple_doc = SimpleDoc()
        simple_doc.page_content = text
        docs = [simple_doc]
        if 'temp_csv' in locals():
            os.unlink(temp_csv.name)
    
    else:
        # Si el tipo no coincide, asumimos un archivo de texto simple
        with open(doc_path, 'r', encoding='utf-8') as f:
            text = f.read()
        class SimpleDoc:
            pass
        simple_doc = SimpleDoc()
        simple_doc.page_content = text
        docs = [simple_doc]
    
    if metadata is not None:
        for doc in docs:
            doc.metadata = metadata
    clear_blank_lines(docs)
    
    # Limpiar archivo temporal de PDF si fue creado
    if 'temp_pdf' in locals():
        os.unlink(temp_pdf.name)
    
    return docs
