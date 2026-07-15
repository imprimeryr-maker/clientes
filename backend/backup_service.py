import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / "backups"
GIT_REMOTE = os.environ.get("GIT_REMOTE", "origin")
GIT_BRANCH = os.environ.get("GIT_BRANCH", "main")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

REPO_DIR = Path(__file__).parent.parent
DB_PATH = REPO_DIR / "data" / "ryr.db"


def log(msg):
    print(f"[backup] {msg}", flush=True)


def export_cliente_backup(cliente_data: dict = None):
    repo_url = f"https://github.com/imprimeryr-maker/clientes.git"

    log("=== INICIO BACKUP ===")

    if not GITHUB_TOKEN:
        log("GITHUB_TOKEN no configurado, se omite backup")
        return

    token_preview = GITHUB_TOKEN[:6] + "..." if len(GITHUB_TOKEN) > 6 else "?"
    log(f"Token GITHUB_TOKEN configurado ({token_preview})")

    if not DB_PATH.exists():
        log(f"ERROR: DB no encontrada en {DB_PATH}")
        return
    log(f"DB encontrada en {DB_PATH} ({DB_PATH.stat().st_size} bytes)")

    git_path = shutil.which("git")
    if not git_path:
        log("ERROR: git no está instalado en el contenedor")
        return
    log(f"git encontrado en {git_path}")

    git_dir = REPO_DIR / ".git"
    if not git_dir.exists():
        log(f"ERROR: directorio .git no existe en {REPO_DIR}")
        return
    log("directorio .git encontrado")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"ryr_{timestamp}.db"
    filepath = BACKUP_DIR / filename

    try:
        shutil.copy2(str(DB_PATH), str(filepath))
        log(f"DB copiada a {filepath}")
    except Exception as e:
        log(f"ERROR copiando DB: {e}")
        return

    try:
        r = subprocess.run(["git", "config", "user.name", "backup-bot"],
                           cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            log(f"git config user.name: {r.stderr.strip()}")

        r = subprocess.run(["git", "config", "user.email", "backup@bot.local"],
                           cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            log(f"git config user.email: {r.stderr.strip()}")

        r = subprocess.run(["git", "add", str(filepath)],
                           cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
        log(f"git add: retcode={r.returncode}")
        if r.returncode != 0:
            log(f"git add stderr: {r.stderr.strip()}")
            return

        r = subprocess.run(["git", "commit", "-m", f"Backup DB: {filename}"],
                           cwd=REPO_DIR, capture_output=True, text=True, timeout=10)
        log(f"git commit: retcode={r.returncode}")
        if r.returncode != 0:
            log(f"git commit: {r.stdout.strip()}")

        r = subprocess.run(
            ["git", "remote", "set-url", GIT_REMOTE,
             f"https://{GITHUB_TOKEN}@github.com/imprimeryr-maker/clientes.git"],
            cwd=REPO_DIR, capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            log(f"git remote set-url: {r.stderr.strip()}")

        r = subprocess.run(["git", "push", GIT_REMOTE, GIT_BRANCH],
                           cwd=REPO_DIR, capture_output=True, text=True, timeout=30)
        log(f"git push: retcode={r.returncode}")
        log(f"git push stdout: {r.stdout.strip()}")
        if r.returncode != 0:
            log(f"git push stderr: {r.stderr.strip()}")
            log("ERROR: el push a GitHub falló")
        else:
            log("=== BACKUP COMPLETADO Y SUBIDO A GITHUB ===")
    except subprocess.TimeoutExpired:
        log("ERROR: git push tardó más de 30 segundos, timeout")
    except Exception as e:
        log(f"ERROR en git push: {e}")
