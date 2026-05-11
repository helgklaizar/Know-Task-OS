import os
from pathlib import Path
from qdrant_client import QdrantClient
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.core.llm import get_llm_and_embeddings
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "docs"
QDRANT_PATH = str(Path(__file__).parent.parent.parent / "qdrant_storage")
COLLECTION_NAME = "knowledge_mesh_core"

def ingest_data():
    print(f"Loading markdown files from {DATA_DIR}...")
    loader = DirectoryLoader(str(DATA_DIR), glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found.")
        return
        
    print(f"Loaded {len(documents)} documents. Chunking...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # 3. Инициализация Embeddings (через Factory)
    _, embeddings = get_llm_and_embeddings()
    
    # Create collection if not exists (using Qdrant native approach or Langchain wrapper)
    # Здесь для простоты используем LangChain Qdrant vector store
    from langchain_community.vectorstores import Qdrant
    
    print("Uploading to local Qdrant storage...")
    qdrant = Qdrant.from_documents(
        chunks,
        embeddings,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME
    )
    print("Ingestion complete! Data is ready for RAG.")

if __name__ == "__main__":
    ingest_data()
