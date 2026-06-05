import hashlib
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "ryr.db")


def _get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL DEFAULT '',
            nombre TEXT NOT NULL DEFAULT '',
            telefono TEXT DEFAULT '',
            correo TEXT DEFAULT '',
            rut TEXT DEFAULT '',
            estado_civil TEXT DEFAULT '',
            profesion TEXT DEFAULT '',
            objetivo TEXT DEFAULT '',
            sub_objetivo TEXT DEFAULT '',
            regimen_matrimonial TEXT DEFAULT '',
            direccion TEXT DEFAULT '',
            ingresos TEXT DEFAULT '{}',
            capacidad_inversion TEXT DEFAULT '{}',
            deudas TEXT DEFAULT '[]',
            activos TEXT DEFAULT '[]',
            cuentas TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()

    try:
        conn2 = _get_conn()
        conn2.execute("ALTER TABLE clientes ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
        conn2.commit()
        conn2.close()
    except Exception:
        pass


def _hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return key.hex() == key_hex


def _row_to_dict(row):
    d = dict(row)
    for key in ("ingresos", "capacidad_inversion", "deudas", "activos", "cuentas"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


_init_db()

# ========== USUARIOS ==========

def crear_usuario(username: str, password: str):
    user_id = str(uuid.uuid4())
    password_hash = _hash_password(password)
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO usuarios (id, username, password_hash) VALUES (?, ?, ?)",
            (user_id, username, password_hash),
        )
        conn.commit()
        return {"id": user_id, "username": username}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def autenticar_usuario(username: str, password: str):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row and _verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def get_usuario(user_id: str):
    conn = _get_conn()
    row = conn.execute(
        "SELECT id, username, created_at FROM usuarios WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ========== SESSIONS ==========

def crear_session(user_id: str):
    session_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(48)
    conn = _get_conn()
    conn.execute(
        "INSERT INTO sessions (id, user_id, token) VALUES (?, ?, ?)",
        (session_id, user_id, token),
    )
    conn.commit()
    conn.close()
    return {"id": session_id, "token": token}


def get_session_by_token(token: str):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def eliminar_session(token: str):
    conn = _get_conn()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


# ========== CLIENTES ==========

def get_clientes(user_id: str):
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM clientes WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_cliente(cliente_id: str, user_id: str):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM clientes WHERE id = ? AND user_id = ?", (cliente_id, user_id)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def create_cliente(data: dict, user_id: str):
    cliente_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        """INSERT INTO clientes (id, user_id, nombre, telefono, correo, rut, estado_civil, regimen_matrimonial, profesion,
           objetivo, sub_objetivo, direccion, ingresos, capacidad_inversion, deudas, activos, cuentas, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            cliente_id,
            user_id,
            data.get("nombre", ""),
            data.get("telefono", ""),
            data.get("correo", ""),
            data.get("rut", ""),
            data.get("estado_civil", ""),
            data.get("regimen_matrimonial", ""),
            data.get("profesion", ""),
            data.get("objetivo", ""),
            data.get("sub_objetivo", ""),
            data.get("direccion", ""),
            json.dumps(data.get("ingresos", {}), ensure_ascii=False),
            json.dumps(data.get("capacidad_inversion", {}), ensure_ascii=False),
            json.dumps(data.get("deudas", []), ensure_ascii=False),
            json.dumps(data.get("activos", []), ensure_ascii=False),
            json.dumps(data.get("cuentas", []), ensure_ascii=False),
            created_at,
        ),
    )
    conn.commit()
    conn.close()
    result = dict(data)
    result.update({"id": cliente_id, "user_id": user_id, "created_at": created_at})
    return result


def update_cliente(cliente_id, user_id, **kwargs):
    conn = _get_conn()
    updates = []
    values = []
    json_fields = {"ingresos", "capacidad_inversion", "deudas", "activos", "cuentas"}
    for k, v in kwargs.items():
        if k in json_fields and not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        updates.append(f"{k} = ?")
        values.append(v)
    values.append(cliente_id)
    values.append(user_id)
    conn.execute(f"UPDATE clientes SET {', '.join(updates)} WHERE id = ? AND user_id = ?", values)
    conn.commit()
    conn.close()


def delete_cliente(cliente_id, user_id):
    conn = _get_conn()
    conn.execute("DELETE FROM clientes WHERE id = ? AND user_id = ?", (cliente_id, user_id))
    conn.commit()
    conn.close()
