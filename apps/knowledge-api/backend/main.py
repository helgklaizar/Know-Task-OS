from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend.services.rag import rag_service
from backend.services.agent import run_agent

app = FastAPI(
    title="Enterprise Agentic Knowledge Mesh",
    description="Multi-agent RAG System API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    user_id: str | None = "default_user"

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    context: list[dict]

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "knowledge-mesh-api"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        # Пропускаем запрос через оркестратора (LangGraph) с поддержкой памяти
        thread_id = request.user_id if request.user_id else "default_thread"
        answer = run_agent(request.query, thread_id)
        return ChatResponse(
            answer=answer,
            sources=[] # В рамках демо LangGraph пока отдает только текст
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    try:
        results = rag_service.search(request.query)
        return SearchResponse(context=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
