import asyncio
import time
from typing import Callable
from agents.antigravity_context import AntigravityContextBuilder
import subprocess
import json
import os
import glob
from telemetry import log_agent_execution

def load_dynamic_skills(task_title: str, task_desc: str) -> str:
    """Dynamically loads relevant skills from the global Antigravity registry."""
    skills_dir = os.path.expanduser("~/.gemini/antigravity/skills")
    loaded_skills = []
    if os.path.exists(skills_dir):
        task_text = f"{task_title} {task_desc}".lower()
        for skill_path in glob.glob(f"{skills_dir}/**/SKILL.md", recursive=True):
            skill_name = os.path.basename(os.path.dirname(skill_path))
            if skill_name.lower() in task_text:
                try:
                    with open(skill_path, "r", encoding="utf-8") as f:
                        loaded_skills.append(f"--- SKILL INJECTED: {skill_name.upper()} ---\n{f.read()}")
                except Exception:
                    pass
    return "\n\n".join(loaded_skills)

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

    # Load Dynamic Skills
    dynamic_skills = load_dynamic_skills(title, description)
    if dynamic_skills:
        system_prompt += f"\n\n{dynamic_skills}"
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "System",
            "actionType": "system",
            "message": "Dynamically injected required skills into the agent's context."
        })
    await asyncio.sleep(1.5)
    log_callback({
        "timestamp": time.strftime("%H:%M:%S"),
        "agent": "Knowledge",
        "actionType": "system",
        "message": f"Loaded workflow '{workflow_to_load}' and RAG context."
    })
    
    # STEP 2 & 3: Execution and Security Check Loop (Cross-Agent Negotiation)
    max_retries = 3
    security_feedback = ""
    
    for attempt in range(max_retries):
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "Developer",
            "actionType": "thought",
            "message": f"Execution attempt {attempt + 1}/{max_retries}. Waking up Apple MLX Engine..."
        })
        
        try:
            from mlx_lm import load, generate
            
            model_name = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
            model, tokenizer = load(model_name)
            
            prompt = f"{system_prompt}\n\nTask: {title}\nDescription: {description}\nRAG Context: {rag_context}"
            if security_feedback:
                prompt += f"\n\nSECURITY REJECTION FEEDBACK. You must fix the following issues:\n{security_feedback}"
                
            prompt += "\n\nPlease generate the required code changes."
            
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "Developer",
                "actionType": "thought",
                "message": "Generating code natively on unified memory (MPS)..."
            })
            
            start_time = time.time()
            response = generate(model, tokenizer, prompt=prompt, max_tokens=1024, verbose=False)
            ttft_ms = (time.time() - start_time) * 1000
            
            # Telemetry Log
            log_agent_execution(task_id, "Developer", ttft_ms, len(response) // 4, success=True, retries=attempt)
            
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
                log_agent_execution(task_id, "Gatekeeper", 0.0, 0, success=True, retries=attempt)
                break  # Success! Exit loop.
            else:
                log_callback({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "agent": "Gatekeeper",
                    "actionType": "error",
                    "message": f"Task rejected: Aegis found {len(findings)} security violations! Sending feedback to Developer..."
                })
                log_agent_execution(task_id, "Gatekeeper", 0.0, 0, success=False, retries=attempt)
                security_feedback = json.dumps(findings, indent=2)
                
        except subprocess.CalledProcessError as e:
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "Gatekeeper",
                "actionType": "error",
                "message": f"Gatekeeper crash: {e.stderr}"
            })
            break  # Fatal error, stop loop
            
    else:
        # STUCK PROTOCOL 2.0
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "System",
            "actionType": "warning",
            "message": f"Task stuck after {max_retries} attempts. Initiating Stuck Protocol 2.0..."
        })
        log_agent_execution(task_id, "System", 0.0, 0, success=False, retries=max_retries)
        
        # Invoke Knowledge Agent for emergency consultation
        try:
            emergency_query = f"The developer agent is stuck trying to fix these security violations: {security_feedback}. Provide an exact code fix strategy."
            resp = httpx.post("http://localhost:8000/api/search", json={"query": emergency_query}, timeout=10.0)
            results = resp.json().get("context", [])
            emergency_context = "\n\n".join([r['content'] for r in results])
            
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "Knowledge",
                "actionType": "thought",
                "message": f"Emergency context retrieved. Escalating to Human-in-the-loop with suggested fix strategy."
            })
            
            # Write emergency context to worktree for human review
            with open(os.path.join(worktree_path, "EMERGENCY_FIX_STRATEGY.md"), "w") as f:
                f.write(f"# Stuck Protocol 2.0 Escalation\n\n## Failing Violations\n{security_feedback}\n\n## Suggested Knowledge Base Strategy\n{emergency_context}")
                
        except Exception as e:
            log_callback({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": "System",
                "actionType": "error",
                "message": f"Knowledge agent offline: {e}"
            })
            
        log_callback({
            "timestamp": time.strftime("%H:%M:%S"),
            "agent": "System",
            "actionType": "error",
            "message": "Human-in-the-loop intervention required. Check EMERGENCY_FIX_STRATEGY.md in the worktree."
        })

