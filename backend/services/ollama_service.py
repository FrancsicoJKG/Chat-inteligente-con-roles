"""
services/ollama_service.py — Comunicación con Ollama
=====================================================
Maneja todas las llamadas a la API REST local de Ollama.
Ollama corre en http://localhost:11434 por defecto.

Documentación Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import httpx
import json
from typing import AsyncGenerator, Optional

OLLAMA_BASE_URL = "http://localhost:11434"
TIMEOUT_SEGUNDOS = 120  # Modelos locales pueden ser lentos


async def chat_completo(
    modelo: str,
    mensajes: list[dict],
    temperatura: float = 0.7,
) -> str:
    """
    Envía una conversación a Ollama y retorna la respuesta completa.
    Útil para respuestas cortas o APIs síncronas.

    Args:
        modelo:      Nombre del modelo (ej. 'llama3', 'mistral', 'gemma2')
        mensajes:    Lista de mensajes [{role, content}, ...]
        temperatura: 0.0 = determinístico, 1.0 = creativo

    Returns:
        Texto de respuesta del modelo

    Raises:
        httpx.ConnectError: Si Ollama no está corriendo
        Exception: Si el modelo no está disponible
    """
    payload = {
        "model": modelo,
        "messages": mensajes,
        "stream": False,
        "options": {
            "temperature": temperatura,
            "num_ctx": 4096,       # Ventana de contexto
        },
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as client:
        try:
            respuesta = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
            return datos["message"]["content"]

        except httpx.ConnectError:
            raise Exception(
                "No se puede conectar a Ollama. "
                "¿Está corriendo? Ejecuta: ollama serve"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(
                    f"Modelo '{modelo}' no encontrado. "
                    f"Descárgalo con: ollama pull {modelo}"
                )
            raise Exception(f"Error de Ollama: {e.response.text}")


async def chat_streaming(
    modelo: str,
    mensajes: list[dict],
    temperatura: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    Envía una conversación a Ollama y retorna tokens en streaming.
    Ideal para respuestas largas con efecto 'typing'.

    Uso (en un endpoint FastAPI con StreamingResponse):
        async for token in chat_streaming(...):
            yield token

    Args:
        modelo:      Nombre del modelo
        mensajes:    Historial de mensajes
        temperatura: Creatividad del modelo

    Yields:
        Tokens de texto uno a uno
    """
    payload = {
        "model": modelo,
        "messages": mensajes,
        "stream": True,
        "options": {
            "temperature": temperatura,
            "num_ctx": 4096,
        },
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
        ) as response:
            async for linea in response.aiter_lines():
                if linea.strip():
                    try:
                        datos = json.loads(linea)
                        token = datos.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if datos.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue


async def listar_modelos_disponibles() -> list[str]:
    """
    Consulta qué modelos están instalados en Ollama.

    Returns:
        Lista de nombres de modelos (ej. ['llama3:latest', 'mistral:latest'])
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            datos = resp.json()
            return [m["name"] for m in datos.get("models", [])]
        except httpx.ConnectError:
            return []


async def verificar_ollama() -> dict:
    """
    Verifica que Ollama esté activo y retorna información del sistema.

    Returns:
        Dict con estado y modelos disponibles
    """
    modelos = await listar_modelos_disponibles()
    if modelos:
        return {
            "activo": True,
            "url": OLLAMA_BASE_URL,
            "modelos": modelos,
            "mensaje": f"{len(modelos)} modelo(s) disponible(s)",
        }
    else:
        return {
            "activo": False,
            "url": OLLAMA_BASE_URL,
            "modelos": [],
            "mensaje": "Ollama no responde. Ejecuta: ollama serve",
        }
