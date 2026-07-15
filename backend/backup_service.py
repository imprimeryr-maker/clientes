import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / "backups"
GIT_REMOTE = os.environ.get("GIT_REMOTE", "origin")
GIT_BRANCH = os.environ.get("GIT_BRANCH", "main")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

REPO_DIR = Path(__file__).parent.parent
DB_PATH = REPO_DIR / "data" / "ryr.db"


def export_cliente_backup(cliente_data: dict = None):
    if not GITHUB_TOKEN:
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"ryr_{timestamp}.db"
    filepath = BACKUP_DIR / filename

    try:
        shutil.copy2(str(DB_PATH), str(filepath))
    except Exception as e:
        print(f"[backup] Error copiando DB: {e}")
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
            ["git", "commit", "-m", f"Backup DB: {filepath.name}"],
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
