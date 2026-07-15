import json
import os
import subprocess
import threading
import time
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / "backups" / "clientes"
GIT_REMOTE = os.environ.get("GIT_REMOTE", "origin")
GIT_BRANCH = os.environ.get("GIT_BRANCH", "main")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

REPO_DIR = Path(__file__).parent.parent


def export_cliente_backup(cliente_data: dict):
    if not GITHUB_TOKEN:
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    client_id = cliente_data.get("id", "unknown")
    filename = f"cliente_{client_id}_{timestamp}.json"
    filepath = BACKUP_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cliente_data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"[backup] Error escribiendo JSON: {e}")
        return

    thread = threading.Thread(target=_git_commit_and_push, args=(filepath,), daemon=True)
    thread.start()


def _git_commit_and_push(filepath: Path):
    try:
        subprocess.run(
            ["git", "config", "user.name", "backup-bot"],
            cwd=REPO_DIR, capture_output=True, timeout=10
        )
        subprocess.run(
            ["git", "config", "user.email", "backup@bot.local"],
            cwd=REPO_DIR, capture_output=True, timeout=10
        )
        subprocess.run(
            ["git", "add", str(filepath)],
            cwd=REPO_DIR, capture_output=True, timeout=10
        )
        subprocess.run(
            ["git", "commit", "-m", f"Backup automático: {filepath.name}"],
            cwd=REPO_DIR, capture_output=True, timeout=10
        )
        subprocess.run(
            [
                "git", "remote", "set-url", GIT_REMOTE,
                f"https://{GITHUB_TOKEN}@github.com/imprimeryr-maker/clientes.git"
            ],
            cwd=REPO_DIR, capture_output=True, timeout=10
        )
        result = subprocess.run(
            ["git", "push", GIT_REMOTE, GIT_BRANCH],
            cwd=REPO_DIR, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"[backup] Error en git push:\n{result.stderr}")
        else:
            print(f"[backup] Backup subido: {filepath.name}")
    except Exception as e:
        print(f"[backup] Error en git push: {e}")
