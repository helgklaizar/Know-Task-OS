import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "knowledge-mesh-api"}

def test_chat_endpoint_rag():
    # Testing a standard question (router should direct to RAG Agent)
    response = client.post(
        "/api/chat",
        json={"query": "What is the Antigravity system?", "user_id": "test_user_1"}
    )
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert "answer" in data
    # Since we use the LLM Factory with a fallback to FakeLLM,
    # we check that the agent at least returns an answer without crashing.
    assert len(data["answer"]) > 0

def test_chat_endpoint_github_fallback():
    # Testing a code-related question (router should direct to GitHub Agent)
    response = client.post(
        "/api/chat",
        json={"query": "Check my code and PR", "user_id": "test_user_2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    
    # We expect that without keys in .env, the GitHub Agent will issue a warning, 
    # rather than crashing with a 500 error.
    assert "[GitHub Agent]" in data["answer"]
