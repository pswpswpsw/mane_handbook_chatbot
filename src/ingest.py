import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from cloud_storage import CloudStorageManager
import tempfile

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
DATA_PATH = "data/MANE_GRADUATE_HANDBOOK.pdf"
DB_PATH = "chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Cloud storage configuration
USE_CLOUD_STORAGE = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
CLOUD_DOCUMENT_PATH = os.getenv("CLOUD_DOCUMENT_PATH", "documents/MANE_GRADUATE_HANDBOOK.pdf")

def load_documents():
    """Loads text from the specified PDF file (local or cloud)."""
    if USE_CLOUD_STORAGE:
        return load_documents_from_cloud()
    else:
        return load_documents_from_local()

def load_documents_from_local():
    """Loads text from local PDF file."""
    if not os.path.exists(DATA_PATH):
        print(f"Error: The file '{DATA_PATH}' was not found.")
        print("Please place the MANE Graduate Student Handbook PDF in the 'data' directory.")
        return None
    
    doc = fitz.open(DATA_PATH)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return [{"page_content": text, "metadata": {"source": DATA_PATH}}]

def load_documents_from_cloud():
    """Loads text from cloud PDF file."""
    try:
        storage_manager = CloudStorageManager()
        
        if not storage_manager.file_exists(CLOUD_DOCUMENT_PATH):
            print(f"Error: The file '{CLOUD_DOCUMENT_PATH}' was not found in cloud storage.")
            return None
        
        # Download to temporary file
        temp_file_path = storage_manager.get_temp_file(CLOUD_DOCUMENT_PATH)
        
        doc = fitz.open(temp_file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return [{"page_content": text, "metadata": {"source": f"gs://{storage_manager.bucket_name}/{CLOUD_DOCUMENT_PATH}"}}]
    
    except Exception as e:
        print(f"Error loading document from cloud storage: {e}")
        return None

def create_vector_database():
    """Creates a ChromaDB vector database from the handbook."""
    print("Loading handbook...")
    documents = load_documents()
    if not documents:
        return

    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    texts = text_splitter.create_documents(
        [doc["page_content"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )

    print(f"Creating embeddings with '{EMBEDDING_MODEL}'. This may take a moment...")
    # Use HuggingFaceEmbeddings for local, free embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print(f"Creating and persisting vector store at '{DB_PATH}'...")
    # Create a new Chroma database from the documents
    db = Chroma.from_documents(
        texts,
        embeddings,
        persist_directory=DB_PATH
    )
    
    print("\n-----------------------------------------")
    print("Vector database created successfully!")
    print(f"Number of chunks: {len(texts)}")
    print(f"Database location: {DB_PATH}")
    if USE_CLOUD_STORAGE:
        print(f"Document source: Cloud Storage ({CLOUD_DOCUMENT_PATH})")
    else:
        print(f"Document source: Local ({DATA_PATH})")
    print("-----------------------------------------")

if __name__ == "__main__":
    create_vector_database()
