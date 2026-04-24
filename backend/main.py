"""
Chat Inteligente con Roles — Backend FastAPI
============================================
Servidor principal. Levanta la API REST que conecta
los clientes (web, WhatsApp, Telegram) con Ollama.

Ejecutar:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, roles, context, health

app = FastAPI(
    title="Chat Inteligente con Roles",
    description="API REST para chat con IA usando roles y contexto personalizable",
    version="1.0.0",
)

# ── CORS: permite peticiones desde el frontend Ionic / web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En producción: especifica tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar routers
app.include_router(health.router,  prefix="/api",  tags=["Health"])
app.include_router(roles.router,   prefix="/api",  tags=["Roles"])
app.include_router(context.router, prefix="/api",  tags=["Contexto"])
app.include_router(chat.router,    prefix="/api",  tags=["Chat"])

@app.get("/")
async def root():
    return {
        "proyecto": "Chat Inteligente con Roles",
        "version": "1.0.0",
        "docs": "/docs",
        "estado": "activo",
    }
