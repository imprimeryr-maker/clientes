from fastapi import APIRouter, Depends, HTTPException
from backend.database import (
    get_clientes as db_get_clientes,
    get_cliente as db_get_cliente,
    create_cliente as db_create_cliente,
    update_cliente as db_update_cliente,
    delete_cliente as db_delete_cliente,
)
from backend.models import ClienteCreate, ClienteUpdate
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("")
def listar_clientes(usuario: dict = Depends(get_current_user)):
    return db_get_clientes(usuario["id"])


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: str, usuario: dict = Depends(get_current_user)):
    c = db_get_cliente(cliente_id, usuario["id"])
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c


@router.post("")
def crear_cliente(body: ClienteCreate, usuario: dict = Depends(get_current_user)):
    data = body.model_dump()
    return db_create_cliente(data, usuario["id"])


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: str, body: ClienteUpdate, usuario: dict = Depends(get_current_user)):
    existing = db_get_cliente(cliente_id, usuario["id"])
    if not existing:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    if kwargs:
        db_update_cliente(cliente_id, usuario["id"], **kwargs)
    return db_get_cliente(cliente_id, usuario["id"])


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: str, usuario: dict = Depends(get_current_user)):
    existing = db_get_cliente(cliente_id, usuario["id"])
    if not existing:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db_delete_cliente(cliente_id, usuario["id"])
    return {"ok": True}
