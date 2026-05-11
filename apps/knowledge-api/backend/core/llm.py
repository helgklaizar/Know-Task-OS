import os
import logging
from langchain_community.embeddings import FakeEmbeddings, OllamaEmbeddings
from langchain_community.llms.fake import FakeListLLM
from langchain_community.llms import Ollama
from langchain_community.llms.mlx_pipeline import MLXPipeline
import requests

def get_llm_and_embeddings():
    """
    Factory method to initialize Local LLM and Embeddings.
    Defaults to Ollama. If Ollama is not available, falls back to Fake implementations.
    """
    try:
        # 1. Проверяем, включен ли хардкорный MLX режим
        if os.getenv("MLX_ENABLED") == "true":
            logging.info("🚀 MLX Mode Enabled! Using Native Apple Silicon GPU via mlx-lm")
            llm = MLXPipeline.from_model_id(
                "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
                pipeline_kwargs={"max_tokens": 512}
            )
            # Эмбеддинги пока оставляем от Ollama или используем фейковые
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            return llm, embeddings

        # 2. Проверяем, запущен ли демон Ollama
        requests.get("http://localhost:11434", timeout=1)
        
        # Пытаемся использовать Ollama
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        llm = Ollama(model="llama3")
        return llm, embeddings
    except Exception as e:
        logging.warning(f"Ollama is not responding. Falling back to FakeLLM. Install Ollama to unlock true Local-First AI. Error: {e}")
        
        embeddings = FakeEmbeddings(size=1536)
        llm = FakeListLLM(responses=["[Локальная Модель] Антигравити — это локальная ИИ-экосистема. Установи Ollama (brew install ollama) и запусти 'ollama run llama3', чтобы этот ответ генерировался по-настоящему."])
        return llm, embeddings
