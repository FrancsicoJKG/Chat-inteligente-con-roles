"""
services/historial_service.py — Gestión del historial de conversaciones
=======================================================================
Almacena el historial en memoria durante la sesión y lo persiste en JSON.
Diseñado para presupuesto $0: sin base de datos externa.

Estructura de un mensaje:
    {
        "role": "user" | "assistant" | "system",
        "content": "texto del mensaje",
    }
"""

import json
import os
from datetime import datetime
from typing import Optional

# Directorio donde se guardan los historiales
HISTORIAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "historiales")
os.makedirs(HISTORIAL_DIR, exist_ok=True)

# Caché en memoria: { sesion_id: [mensajes] }
_historial_memoria: dict[str, list[dict]] = {}

MAX_MENSAJES_CONTEXTO = 20  # Cuántos mensajes se envían al LLM (para no exceder contexto)


def obtener_historial(sesion_id: str) -> list[dict]:
    """
    Retorna el historial completo de una sesión.
    Primero busca en memoria, luego en disco.

    Args:
        sesion_id: ID único de la sesión (ej. "usuario_123_profesor")

    Returns:
        Lista de mensajes [{role, content}, ...]
    """
    if sesion_id in _historial_memoria:
        return _historial_memoria[sesion_id]

    # Intentar cargar desde disco
    ruta = _ruta_sesion(sesion_id)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
            _historial_memoria[sesion_id] = datos.get("mensajes", [])
            return _historial_memoria[sesion_id]

    return []


def agregar_mensaje(sesion_id: str, rol: str, contenido: str) -> None:
    """
    Agrega un mensaje al historial de la sesión.

    Args:
        sesion_id: ID de la sesión
        rol:       'user' o 'assistant'
        contenido: Texto del mensaje
    """
    if sesion_id not in _historial_memoria:
        _historial_memoria[sesion_id] = []

    _historial_memoria[sesion_id].append({
        "role": rol,
        "content": contenido,
        "timestamp": datetime.now().isoformat(),
    })

    # Persistir en disco
    _guardar_en_disco(sesion_id)


def construir_mensajes_para_llm(
    sesion_id: str,
    prompt_sistema: str,
    nueva_pregunta: str,
) -> list[dict]:
    """
    Construye la lista de mensajes que se envía al LLM.
    Incluye: system prompt + historial reciente + nueva pregunta.

    Args:
        sesion_id:       ID de la sesión
        prompt_sistema:  System prompt del rol elegido
        nueva_pregunta:  Pregunta actual del usuario

    Returns:
        Lista de mensajes formateada para Ollama
    """
    historial = obtener_historial(sesion_id)

    # Tomar solo los últimos N mensajes para no exceder contexto
    historial_reciente = historial[-MAX_MENSAJES_CONTEXTO:]

    # Filtrar campos extra que Ollama no necesita (solo role y content)
    mensajes_limpios = [
        {"role": m["role"], "content": m["content"]}
        for m in historial_reciente
        if m["role"] in ("user", "assistant")
    ]

    return [
        {"role": "system", "content": prompt_sistema},
        *mensajes_limpios,
        {"role": "user", "content": nueva_pregunta},
    ]


def limpiar_historial(sesion_id: str) -> None:
    """
    Elimina el historial de una sesión (nueva conversación).

    Args:
        sesion_id: ID de la sesión a limpiar
    """
    _historial_memoria.pop(sesion_id, None)

    ruta = _ruta_sesion(sesion_id)
    if os.path.exists(ruta):
        os.remove(ruta)


def listar_sesiones() -> list[dict]:
    """
    Lista todas las sesiones guardadas en disco.

    Returns:
        Lista de dicts con info de cada sesión
    """
    sesiones = []
    for archivo in os.listdir(HISTORIAL_DIR):
        if archivo.endswith(".json"):
            ruta = os.path.join(HISTORIAL_DIR, archivo)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    sesiones.append({
                        "sesion_id": datos.get("sesion_id"),
                        "rol": datos.get("rol"),
                        "mensajes": len(datos.get("mensajes", [])),
                        "creada": datos.get("creada"),
                        "actualizada": datos.get("actualizada"),
                    })
            except Exception:
                continue

    return sorted(sesiones, key=lambda s: s.get("actualizada", ""), reverse=True)


# ── Funciones internas ──────────────────────────────────────────────────────

def _ruta_sesion(sesion_id: str) -> str:
    """Retorna la ruta del archivo JSON de una sesión"""
    nombre_seguro = sesion_id.replace("/", "_").replace("\\", "_")
    return os.path.join(HISTORIAL_DIR, f"{nombre_seguro}.json")


def _guardar_en_disco(sesion_id: str) -> None:
    """Persiste el historial en memoria al disco"""
    ruta = _ruta_sesion(sesion_id)
    existe = os.path.exists(ruta)

    datos = {
        "sesion_id": sesion_id,
        "rol": sesion_id.split("_")[-1] if "_" in sesion_id else "desconocido",
        "mensajes": _historial_memoria.get(sesion_id, []),
        "creada": datetime.now().isoformat() if not existe else _leer_campo(ruta, "creada"),
        "actualizada": datetime.now().isoformat(),
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def _leer_campo(ruta: str, campo: str) -> Optional[str]:
    """Lee un campo específico de un JSON en disco"""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f).get(campo)
    except Exception:
        return None
