from fastapi import APIRouter
from services.roles_service import listar_roles

router = APIRouter()

@router.get("/roles")
async def obtener_roles():
    return {"roles": listar_roles()}
