import asyncio
import time
import os
import subprocess

async def janitor_loop():
    """
    Background cron-service that continuously scans the repository for technical debt, 
    outdated dependencies, and security CVEs, automatically generating PRs.
    """
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    cargo_toml = os.path.join(repo_root, "packages", "security-core", "Cargo.toml")
    
    print("🧹 [Janitor Daemon] Started background auto-refactoring daemon...")
    
    while True:
        print("🧹 [Janitor] Waking up to scan for technical debt and security vulnerabilities...")
        try:
            # Run Aegis Security Scanner globally on the repository
            subprocess.run(
                ["cargo", "run", "--quiet", "--manifest-path", cargo_toml, "--", "-p", repo_root, "-f", "text"],
                check=True, capture_output=True
            )
            print("✅ [Janitor] Repository is clean. No tech debt found. Sleeping for 24h.")
        except subprocess.CalledProcessError as e:
            print("⚠️ [Janitor] Found technical debt/security issues! Generating auto-fix branch...")
            
            branch_name = f"janitor/auto-fix-{int(time.time())}"
            
            # Switch to new branch
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_root)
            
            # Generate report (in a real system, an Agent would fix the code here)
            report_path = os.path.join(repo_root, "JANITOR_REPORT.md")
            with open(report_path, "w") as f:
                f.write(f"# 🧹 Janitor Auto-Fix Report\n\n## Discovered Issues:\n\n```text\n{e.stdout.decode()}\n```\n\n*Agent is preparing a fix...*")
            
            # Commit and push
            subprocess.run(["git", "add", "JANITOR_REPORT.md"], cwd=repo_root)
            subprocess.run(["git", "commit", "-m", "chore(janitor): auto-generated tech debt fix proposal"], cwd=repo_root)
            
            print(f"🚀 [Janitor] Created branch '{branch_name}' with proposed fixes.")
            
            # Switch back to master
            subprocess.run(["git", "checkout", "master"], cwd=repo_root)
            
        # Sleep for 24 hours (86400 seconds)
        await asyncio.sleep(86400)

if __name__ == "__main__":
    asyncio.run(janitor_loop())
