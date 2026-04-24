"""
routers/chat.py — Endpoint principal del chat
=============================================
POST /api/chat → Procesa una pregunta y retorna respuesta del LLM

Flujo:
  1. Recibe pregunta + rol + sesion_id + contexto
  2. Carga/crea el historial de la sesión
  3. Construye el prompt de sistema según el rol
  4. Envía todo a Ollama y obtiene respuesta
  5. Guarda la respuesta en el historial
  6. Retorna la respuesta al cliente
"""

import uuid
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.roles_service import construir_prompt_sistema
from services.ollama_service import chat_completo
from services.historial_service import (
    construir_mensajes_para_llm,
    agregar_mensaje,
    limpiar_historial,
    listar_sesiones,
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Enviar mensaje al chat")
async def enviar_mensaje(payload: ChatRequest):
    """
    ## Endpoint principal del chat

    Recibe una pregunta del usuario y retorna la respuesta del modelo LLM
    configurado con el rol seleccionado.

    ### Ejemplo de petición:
    ```json
    {
      "pregunta": "¿Cómo funciona el polimorfismo?",
      "rol_id": "programador",
      "modelo": "llama3",
      "sesion_id": "usuario_42"
    }
    ```

    ### Roles disponibles:
    - `profesor` — Explicaciones pedagógicas
    - `programador` — Respuestas técnicas con código
    - `psicologo` — Apoyo emocional empático
    - `negocios` — Consultoría estratégica
    - `agente_empresa` — Atención al cliente con contexto del negocio
    """

    # ── 1. Generar sesion_id si no viene ───────────────────────────────────
    sesion_id = payload.sesion_id or f"sesion_{uuid.uuid4().hex[:8]}_{payload.rol_id}"

    # ── 2. Construir prompt de sistema según rol + contexto ────────────────
    prompt_sistema = construir_prompt_sistema(
        rol_id=payload.rol_id,
        contexto_adicional=payload.contexto_adicional,
    )

    # ── 3. Armar lista de mensajes (sistema + historial + nueva pregunta) ──
    mensajes = construir_mensajes_para_llm(
        sesion_id=sesion_id,
        prompt_sistema=prompt_sistema,
        nueva_pregunta=payload.pregunta,
    )

    # ── 4. Llamar a Ollama ─────────────────────────────────────────────────
    try:
        respuesta_texto = await chat_completo(
            modelo=payload.modelo,
            mensajes=mensajes,
            temperatura=payload.temperatura,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    # ── 5. Guardar en historial ────────────────────────────────────────────
    agregar_mensaje(sesion_id, "user", payload.pregunta)
    agregar_mensaje(sesion_id, "assistant", respuesta_texto)

    # ── 6. Retornar respuesta ──────────────────────────────────────────────
    return ChatResponse(
        respuesta=respuesta_texto,
        rol_id=payload.rol_id,
        sesion_id=sesion_id,
        modelo=payload.modelo,
    )


@router.delete("/chat/{sesion_id}", summary="Limpiar historial de una sesión")
async def limpiar_sesion(sesion_id: str):
    """
    Elimina el historial de conversación de una sesión.
    Útil para 'Nueva conversación'.
    """
    limpiar_historial(sesion_id)
    return {"mensaje": f"Historial de sesión '{sesion_id}' eliminado", "sesion_id": sesion_id}


@router.get("/chat/sesiones", summary="Listar sesiones guardadas")
async def obtener_sesiones():
    """
    Lista todas las conversaciones guardadas en disco.
    """
    return {"sesiones": listar_sesiones()}
