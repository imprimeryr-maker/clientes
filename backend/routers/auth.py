from fastapi import APIRouter, Depends, HTTPException, Header
from backend.database import (
    crear_usuario,
    autenticar_usuario,
    crear_session,
    get_session_by_token,
    eliminar_session,
    get_usuario,
)
from backend.models import UsuarioCreate, UsuarioLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization[7:]
    session = get_session_by_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    usuario = get_usuario(session["user_id"])
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/register")
def register(body: UsuarioCreate):
    if not body.username or len(body.username) < 3:
        raise HTTPException(status_code=400, detail="Usuario debe tener al menos 3 caracteres")
    if not body.password or len(body.password) < 4:
        raise HTTPException(status_code=400, detail="Contraseña debe tener al menos 4 caracteres")
    usuario = crear_usuario(body.username, body.password)
    if not usuario:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    return usuario


@router.post("/login")
def login(body: UsuarioLogin):
    usuario = autenticar_usuario(body.username, body.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    session = crear_session(usuario["id"])
    return {"token": session["token"], "usuario": {"id": usuario["id"], "username": usuario["username"]}}


@router.get("/me")
def me(usuario: dict = Depends(get_current_user)):
    return usuario


@router.post("/logout")
def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        eliminar_session(token)
    return {"ok": True}
