"""
routers/context.py — Gestión de contextos de negocio/usuario
=============================================================
Permite guardar y cargar contextos (catálogos, políticas, FAQs, etc.)
que se inyectan en el prompt del agente.
"""

import os, json, uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.schemas import ContextoRequest, ContextoGuardado

router = APIRouter()

CONTEXTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "contextos")
os.makedirs(CONTEXTOS_DIR, exist_ok=True)


@router.post("/contexto", response_model=ContextoGuardado, summary="Guardar contexto")
async def guardar_contexto(payload: ContextoRequest):
    """
    Guarda un contexto (info de empresa, perfil de usuario, etc.)
    que se puede usar en las conversaciones del agente.

    ### Ejemplo para agente empresarial:
    ```json
    {
      "nombre": "Tienda TechGT",
      "tipo": "empresarial",
      "contenido": "Somos una tienda de tecnología en Guatemala...
        Productos: laptops, celulares, accesorios.
        Horario: Lunes a Sábado 9am-6pm.
        WhatsApp: +502 5555-0000"
    }
    ```
    """
    ctx_id = f"ctx_{uuid.uuid4().hex[:8]}"
    datos = {
        "id": ctx_id,
        "nombre": payload.nombre,
        "tipo": payload.tipo,
        "contenido": payload.contenido,
        "creado": datetime.now().isoformat(),
    }
    with open(os.path.join(CONTEXTOS_DIR, f"{ctx_id}.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    return ContextoGuardado(
        id=ctx_id,
        nombre=payload.nombre,
        tipo=payload.tipo,
        caracteres=len(payload.contenido),
        mensaje=f"Contexto '{payload.nombre}' guardado correctamente. ID: {ctx_id}",
    )


@router.get("/contexto/{ctx_id}", summary="Obtener un contexto por ID")
async def obtener_contexto(ctx_id: str):
    """Carga un contexto guardado por su ID."""
    ruta = os.path.join(CONTEXTOS_DIR, f"{ctx_id}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail=f"Contexto '{ctx_id}' no encontrado")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/contextos", summary="Listar contextos guardados")
async def listar_contextos():
    """Lista todos los contextos disponibles."""
    contextos = []
    for archivo in os.listdir(CONTEXTOS_DIR):
        if archivo.endswith(".json"):
            ruta = os.path.join(CONTEXTOS_DIR, archivo)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    contextos.append({
                        "id": d["id"], "nombre": d["nombre"],
                        "tipo": d["tipo"], "creado": d.get("creado"),
                        "caracteres": len(d.get("contenido", "")),
                    })
            except Exception:
                continue
    return {"contextos": contextos}


@router.delete("/contexto/{ctx_id}", summary="Eliminar un contexto")
async def eliminar_contexto(ctx_id: str):
    """Elimina un contexto guardado."""
    ruta = os.path.join(CONTEXTOS_DIR, f"{ctx_id}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail=f"Contexto '{ctx_id}' no encontrado")
    os.remove(ruta)
    return {"mensaje": f"Contexto '{ctx_id}' eliminado"}
