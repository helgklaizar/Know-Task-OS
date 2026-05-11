from pathlib import Path
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from backend.core.llm import get_llm_and_embeddings
import logging

QDRANT_PATH = str(Path(__file__).parent.parent.parent / "qdrant_storage")
COLLECTION_NAME = "knowledge_mesh_core"

class RAGService:
    def __init__(self):
        # 1. Подключаемся к локальному хранилищу
        self.client = QdrantClient(path=QDRANT_PATH)
        
        # Интеллектуальный выбор провайдера (Local-First: Ollama -> Fake)
        self.llm, self.embeddings = get_llm_and_embeddings()
        
        # 2. Инициализируем Vector Store
        self.vector_store = Qdrant(
            client=self.client,
            collection_name=COLLECTION_NAME,
            embeddings=self.embeddings
        )
        
        # 3. Настраиваем Retriever (поиск топ-3 кусков)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        
        # 5. Собираем Промпт
        template = """Ты — интеллектуальный агент корпоративной базы знаний (Knowledge Mesh).
Используй предоставленный ниже контекст для ответа на вопрос пользователя.
Если ответа нет в контексте, честно скажи, что не знаешь, не выдумывай (no hallucinations).
Отвечай структурированно, профессионально и по делу.

Контекст:
{context}

Вопрос: {question}

Ответ:"""
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # 6. Собираем LangChain LCEL Pipeline
        self.chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ask(self, query: str) -> dict:
        # Получаем исходные документы (чтобы вернуть их как sources)
        docs = self.retriever.invoke(query)
        sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
        
        # Генерируем ответ
        answer = self.chain.invoke(query)
        
        # Убираем дубликаты из sources
        unique_sources = list(set(sources))
        
        return {
            "answer": answer,
            "sources": unique_sources
        }

# Singleton экземпляр для переиспользования в FastAPI
rag_service = RAGService()
