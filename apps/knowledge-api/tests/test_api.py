import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "knowledge-mesh-api"}

def test_chat_endpoint_rag():
    # Тестируем обычный вопрос (роутер должен направить в RAG Agent)
    response = client.post(
        "/api/chat",
        json={"query": "Что такое система Антигравити?", "user_id": "test_user_1"}
    )
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert "answer" in data
    # Так как мы используем LLM Factory с фоллбеком на FakeLLM,
    # мы проверяем, что агент хотя бы отдал ответ без краша.
    assert len(data["answer"]) > 0

def test_chat_endpoint_github_fallback():
    # Тестируем вопрос по коду (роутер должен направить в GitHub Agent)
    response = client.post(
        "/api/chat",
        json={"query": "Проверь мой код и PR", "user_id": "test_user_2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    
    # Мы ожидаем, что без ключей в .env GitHub Agent выдаст предупреждение, 
    # а не упадет с ошибкой 500.
    assert "[GitHub Agent]" in data["answer"]
