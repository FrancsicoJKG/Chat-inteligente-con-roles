from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=4000)
    rol_id: str = Field(default="profesor")
    sesion_id: Optional[str] = None
    modelo: str = Field(default="llama3")
    contexto_adicional: Optional[str] = None
    temperatura: float = Field(default=0.7, ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    respuesta: str
    rol_id: str
    sesion_id: str
    modelo: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ContextoRequest(BaseModel):
    nombre: str
    tipo: str
    contenido: str = Field(..., min_length=10, max_length=10000)

class ContextoGuardado(BaseModel):
    id: str
    nombre: str
    tipo: str
    caracteres: int
    mensaje: str
