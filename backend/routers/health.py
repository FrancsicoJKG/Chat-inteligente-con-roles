from fastapi import APIRouter
from services.ollama_service import verificar_ollama

router = APIRouter()

@router.get("/health")
async def health_check():
    ollama_info = await verificar_ollama()
    return {"api": "activa", "ollama": ollama_info}
