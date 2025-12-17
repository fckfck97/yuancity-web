from langchain_community.document_loaders import Docx2txtLoader

def load_word_document(file_path):
    """
    Carga un archivo Word usando UnstructuredWordDocumentLoader.
    """
    loader = Docx2txtLoader(file_path)
    docs = loader.load()
    return docs