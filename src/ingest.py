import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
DATA_PATH = "data/MANE_GRADUATE_HANDBOOK.pdf"
DB_PATH = "chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def load_documents():
    """Loads text from the specified PDF file."""
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
    print("-----------------------------------------")

if __name__ == "__main__":
    create_vector_database()
