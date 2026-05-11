from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_community.llms.fake import FakeListLLM
import os
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from backend.services.rag import rag_service

# 1. State definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_step: str

# 2. Nodes
def router_node(state: AgentState):
    query = state["messages"][-1].content.lower()
    
    # Очень простая логика маршрутизации для MVP
    if "код" in query or "github" in query or "pr" in query:
        next_step = "github_agent"
    else:
        next_step = "rag_agent"
        
    return {"next_step": next_step}

def rag_agent_node(state: AgentState):
    query = state["messages"][-1].content
    result = rag_service.ask(query)
    
    response = f"[RAG Agent] {result['answer']}\n\nИсточники: {', '.join(result['sources'])}"
    return {"messages": [AIMessage(content=response)]}

def github_agent_node(state: AgentState):
    query = state["messages"][-1].content
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Fallback если нет ключей для реального Tool Calling
    if not github_token or not openai_key:
        return {"messages": [AIMessage(content="[GitHub Agent] ⚠️ Для работы авто-ревьюера установите GITHUB_PERSONAL_ACCESS_TOKEN и OPENAI_API_KEY в .env")]}
    
    try:
        # Инициализация Github API и Тулкита
        github = GitHubAPIWrapper()
        toolkit = GitHubToolkit.from_github_api_wrapper(github)
        tools = toolkit.get_tools()
        
        # Для Tool Use нужен LLM, который нативно поддерживает инструменты (ChatOpenAI или ChatOllama)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Создаем ReAct агента, который умеет пользоваться GitHub Tools
        github_agent = create_react_agent(llm, tools=tools)
        
        # Запускаем вложенного агента
        result = github_agent.invoke({"messages": [HumanMessage(content=query)]})
        response = f"[GitHub Agent] {result['messages'][-1].content}"
        
    except Exception as e:
        response = f"[GitHub Agent] Ошибка интеграции с GitHub API: {str(e)}"
        
    return {"messages": [AIMessage(content=response)]}

# 3. Edges mapping
def route_after_router(state: AgentState):
    return state["next_step"]

# 4. Graph construction
builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("rag_agent", rag_agent_node)
builder.add_node("github_agent", github_agent_node)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "rag_agent": "rag_agent",
        "github_agent": "github_agent"
    }
)

builder.add_edge("rag_agent", END)
builder.add_edge("github_agent", END)

# Добавляем память (Chat History)
memory = MemorySaver()

# Скомпилированный LangGraph граф с чекпоинтером
knowledge_mesh_agent = builder.compile(checkpointer=memory)

def run_agent(query: str, thread_id: str = "default_thread") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = knowledge_mesh_agent.invoke({"messages": [HumanMessage(content=query)]}, config)
    return result["messages"][-1].content
