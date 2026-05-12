from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import asyncio
from git_engine import create_task_worktree, PROJECT_ROOT
from agent_runner import run_developer_agent

app = FastAPI(title="AI-Dispatcher Local API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "dispatcher.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            status TEXT,
            agentRole TEXT,
            gitBranch TEXT,
            isStuck BOOLEAN,
            cost REAL
        )
    """)
    conn.commit()
    
    # Check if empty
    cursor.execute("SELECT count(*) FROM cards")
    if cursor.fetchone()[0] == 0:
        # Insert initial data
        initial_data = [
            ("101", "Design Agent Architecture", "Create a plan.", "Done", "Architect", "", False, 0.12),
            ("102", "Setup React Frontend", "Vite project.", "In Progress", "Coder", "feature/task-102", False, 1.45),
            ("105", "Connect Local SQLite", "Need DB credentials to proceed.", "Blocked", "Coder", "feature/task-105", True, 0.0)
        ]
        cursor.executemany("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)", initial_data)
        conn.commit()
    conn.close()

init_db()

class CardModel(BaseModel):
    id: str
    title: str
    description: str
    status: str
    agentRole: Optional[str] = None
    gitBranch: Optional[str] = None
    isStuck: bool = False
    cost: float = 0.0

@app.get("/api/cards", response_model=List[CardModel])
def get_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        CardModel(
            id=r[0], title=r[1], description=r[2], status=r[3],
            agentRole=r[4], gitBranch=r[5], isStuck=bool(r[6]), cost=r[7]
        ) for r in rows
    ]

class CreateCardModel(BaseModel):
    title: str
    description: str

@app.post("/api/cards", response_model=CardModel)
def create_card(card: CreateCardModel):
    import uuid
    card_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cards (id, title, description, status, agentRole, gitBranch, isStuck, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (card_id, card.title, card.description, "Backlog", "Unassigned", "", False, 0.0)
    )
    conn.commit()
    conn.close()
    return CardModel(
        id=card_id, title=card.title, description=card.description, status="Backlog",
        agentRole="Unassigned", gitBranch="", isStuck=False, cost=0.0
    )

class StatusUpdateModel(BaseModel):
    status: str

# Global queue for SSE logs
log_queue = asyncio.Queue()

def push_log(log_entry: dict):
    # Fire and forget pushing to queue
    try:
        log_queue.put_nowait(log_entry)
    except Exception:
        pass

@app.get("/api/logs")
async def sse_logs():
    async def event_generator():
        while True:
            log = await log_queue.get()
            import json
            yield {"data": json.dumps(log)}
            
    return EventSourceResponse(event_generator())

@app.put("/api/cards/{card_id}/status")
def update_card_status(card_id: str, update: StatusUpdateModel, background_tasks: BackgroundTasks):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get card details for agent
    cursor.execute("SELECT title, description FROM cards WHERE id = ?", (card_id,))
    card_data = cursor.fetchone()
    
    # If moved to In Progress, initialize Git Worktree
    branch_name = None
    if update.status == "In Progress":
        try:
            branch_name = create_task_worktree(card_id)
            # Spawn agent in background
            worktree_path = os.path.join(PROJECT_ROOT, "worktrees", f"task-{card_id}")
            if card_data:
                background_tasks.add_task(run_developer_agent, card_id, worktree_path, card_data[0], card_data[1], push_log)
        except Exception as e:
            print(f"Error creating worktree: {e}")
            
    if branch_name:
        cursor.execute("UPDATE cards SET status = ?, gitBranch = ? WHERE id = ?", (update.status, branch_name, card_id))
    else:
        cursor.execute("UPDATE cards SET status = ? WHERE id = ?", (update.status, card_id))
        
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully", "new_status": update.status, "branch": branch_name}

@app.put("/api/cards/{card_id}/unstuck")
def unstuck_card(card_id: str, response: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE cards SET isStuck = 0, status = 'In Progress' WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()
    return {"message": "Agent received human input and resumed work."}
