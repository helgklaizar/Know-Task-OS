import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import NotionDBLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from backend.core.llm import get_llm_and_embeddings

load_dotenv()

QDRANT_PATH = str(Path(__file__).parent.parent.parent / "qdrant_storage")
COLLECTION_NAME = "knowledge_mesh_core"

def ingest_notion(database_id: str):
    """
    Выгружает базу знаний из Notion API, чанкует и отправляет в локальный Qdrant.
    Необходимо задать переменную окружения NOTION_TOKEN.
    """
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("❌ Ошибка: Установите NOTION_TOKEN в .env")
        return

    print(f"📥 Загрузка данных из Notion (Database ID: {database_id})...")
    
    try:
        loader = NotionDBLoader(
            integration_token=token,
            database_id=database_id,
            request_timeout_sec=30,
        )
        documents = loader.load()
    except Exception as e:
        print(f"❌ Ошибка загрузки из Notion: {e}")
        return

    if not documents:
        print("🤷‍♂️ Документы не найдены в базе Notion.")
        return

    print(f"✅ Успешно загружено {len(documents)} документов из Notion. Начинаем чанкинг...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Разбили на {len(chunks)} фрагментов.")

    # Используем нашу общую фабрику (Ollama / MLX / Fake)
    _, embeddings = get_llm_and_embeddings()

    print("🧠 Заливаем вектора в локальный Qdrant...")
    qdrant = Qdrant.from_documents(
        chunks,
        embeddings,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME
    )
    print("🎉 Ингестия Notion успешно завершена! Данные готовы для RAG-агента.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ингестия данных из Notion базы")
    parser.add_argument("--db", type=str, required=True, help="Notion Database ID")
    args = parser.parse_args()
    
    ingest_notion(args.db)
