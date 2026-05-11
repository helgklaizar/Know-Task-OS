import asyncio
import time
from typing import Callable
from agents.antigravity_context import AntigravityContextBuilder
import subprocess
import json
import os

# Omni-Agent Execution Engine
async def run_developer_agent(task_id: str, worktree_path: str, title: str, description: str, log_callback: Callable[[dict], None]):
    """
    Simulates an LLM agent thinking and doing work in the isolated git worktree.
    In a real app, this would use LangChain or OpenAI API.
    """
    
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "System",
        "actionType": "system",
        "message": f"Omni-Agent starting Task #{task_id} in {worktree_path}..."
    })
    
    # STEP 1: Build Context (Antigravity-bar + Knowledge-agent)
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "Knowledge",
        "actionType": "thought",
        "message": f"Building execution context..."
    })
    
    context_builder = AntigravityContextBuilder()
    # Mock detection of workflow type
    workflow_to_load = "feature-pipeline" if "Frontend" in title else "arch-evolution"
    system_prompt = context_builder.build_system_prompt(workflow_name=workflow_to_load)
    
    import httpx
    try:
        query = f"{title} {description}"
        resp = httpx.post("http://localhost:8000/api/search", json={"query": query}, timeout=10.0)
        resp.raise_for_status()
        results = resp.json().get("context", [])
        rag_context = "\n\n".join([f"Source: {r['source']}\n{r['content']}" for r in results])
        if not rag_context:
            rag_context = "No relevant context found in Vector DB."
    except Exception as e:
        rag_context = f"Error fetching from knowledge-api: {e}"

    
    await asyncio.sleep(1.5)
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "Knowledge",
        "actionType": "system",
        "message": f"Loaded workflow '{workflow_to_load}' and RAG context."
    })
    
    # STEP 2: Execution (Local Apple MLX LLM Execution)
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "Developer",
        "actionType": "thought",
        "message": "Waking up Apple MLX Engine (Llama-3 8B 4bit)..."
    })
    
    try:
        from mlx_lm import load, generate
        
        # In a persistent setup, the model would be loaded once at startup.
        # Here we lazy load it for the task.
        model_name = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
        model, tokenizer = load(model_name)
        
        prompt = f"{system_prompt}\n\nTask: {title}\nDescription: {description}\nRAG Context: {rag_context}\n\nPlease generate the required code changes."
        
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Developer",
            "actionType": "thought",
            "message": "Generating code natively on unified memory (MPS)..."
        })
        
        # Generate the response
        response = generate(model, tokenizer, prompt=prompt, max_tokens=1024, verbose=False)
        
        # Mock: Apply the code changes to worktree
        with open(os.path.join(worktree_path, "agent_output.md"), "w") as f:
            f.write(response)
            
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Developer",
            "actionType": "file_change",
            "message": f"Code generated successfully. Wrote {len(response)} chars to worktree."
        })
        
    except ImportError:
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Developer",
            "actionType": "error",
            "message": "mlx_lm not installed. Falling back to mock generation."
        })
        await asyncio.sleep(2)
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Developer",
            "actionType": "file_change",
            "message": "Mock: Modified files in worktree."
        })
    
    # STEP 3: Security & Quality Check (Local-security-agent via Rust)
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "Gatekeeper",
        "actionType": "thought",
        "message": "Invoking Rust Aegis Gatekeeper to scan git diffs..."
    })
    
    cargo_toml = os.path.join(os.path.dirname(__file__), "..", "..", "packages", "security-core", "Cargo.toml")
    
    try:
        process = subprocess.run(
            ["cargo", "run", "--quiet", "--manifest-path", cargo_toml, "--", "-p", worktree_path, "-f", "json"],
            capture_output=True, text=True, check=True
        )
        
        # Parse the JSON output from Rust scanner
        if process.stdout.strip():
            findings = json.loads(process.stdout)
        else:
            findings = []
            
        if len(findings) == 0:
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "Gatekeeper",
                "actionType": "system",
                "message": "Security scan passed. Aegis confirmed 0 leaks."
            })
        else:
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "Gatekeeper",
                "actionType": "error",
                "message": f"Task rejected: Aegis found {len(findings)} security violations!"
            })
    except subprocess.CalledProcessError as e:
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Gatekeeper",
            "actionType": "error",
            "message": f"Gatekeeper crash: {e.stderr}"
        })

