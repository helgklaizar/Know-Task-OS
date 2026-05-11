import time
import json
import os
from datetime import datetime

TELEMETRY_LOG = os.path.join(os.path.dirname(__file__), "telemetry.jsonl")

def log_agent_execution(task_id: str, agent_name: str, ttft_ms: float, tokens_generated: int, success: bool, retries: int):
    """Logs MLOps telemetry data for agent execution."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "task_id": task_id,
        "agent": agent_name,
        "ttft_ms": round(ttft_ms, 2),
        "tokens_generated": tokens_generated,
        "success": success,
        "retries": retries
    }
    with open(TELEMETRY_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
