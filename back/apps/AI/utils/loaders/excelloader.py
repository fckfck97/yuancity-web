from langchain_community.document_loaders import UnstructuredExcelLoader

def load_excel_document(file_path):
    """
    Carga un archivo Excel usando UnstructuredExcelLoader y devuelve la lista de documentos.
    """
    loader = UnstructuredExcelLoader(file_path, mode="elements")
    docs = loader.load()
    
    if isinstance(docs, list):
        combined_text = "\n\n".join([getattr(doc, "page_content", str(doc)) for doc in docs])
        print(f"Documentos cargados desde Excel: {len(docs)}")
        print(f"Texto combinado:\n{combined_text}")
        # Devolver la lista de documentos en lugar del string combinado
        return docs
    else:
        print("Formato inesperado en los documentos cargados.")
        return []
