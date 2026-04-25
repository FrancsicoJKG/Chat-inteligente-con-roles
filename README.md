# Chat Inteligente con Roles IA

Sistema de chat con inteligencia artificial que adapta su comportamiento según el **rol seleccionado** por el usuario. Funciona completamente **local y gratuito**, sin APIs externas ni costos de operación.

Desarrollado con **Ollama** (LLMs locales) + **FastAPI** (backend) + **Frontend Web** + **Bot de Telegram** + **Bot de WhatsApp**.

---

## ¿Cómo funciona?

```
Usuario escribe una pregunta
        ↓
Selecciona un ROL (Profesor / Programador / Psicólogo / Negocios / Agente)
        ↓
FastAPI construye un prompt personalizado con el rol + historial + contexto
        ↓
Ollama ejecuta el modelo LLM localmente (llama3, mistral, gemma2...)
        ↓
El modelo responde con el estilo y enfoque del rol elegido
        ↓
La respuesta llega al usuario (web / Telegram / WhatsApp)
```

El sistema mantiene el **historial de conversación** por sesión, lo que permite conversaciones multi-turno coherentes. Cada canal (web, Telegram, WhatsApp) se conecta a la misma API central.

---

## 🎭 Roles disponibles

| Rol | Icono | Enfoque |
|-----|-------|---------|
| Profesor | 📚 | Explicaciones pedagógicas, analogías, ejercicios |
| Programador | 💻 | Código funcional, buenas prácticas, debugging |
| Psicólogo | 🧠 | Escucha activa, apoyo emocional, orientación |
| Experto en Negocios | 📊 | Estrategia, análisis, planes de acción |
| Agente de Empresa | 🏢 | Atención al cliente con contexto del negocio |

---

## 📁 Estructura del proyecto

```
CHATBOT/
├── backend/
│   ├── main.py                    ← Entrada FastAPI (puerto 8000)
│   ├── requirements.txt           ← Dependencias Python
│   ├── telegram_bot.py            ← Bot de Telegram
│   ├── .env                       ← Tokens y variables (NO se sube a GitHub)
│   ├── routers/
│   │   ├── chat.py                ← POST /api/chat  (endpoint principal)
│   │   ├── roles.py               ← GET  /api/roles
│   │   ├── context.py             ← CRUD /api/contexto
│   │   └── health.py              ← GET  /api/health
│   ├── services/
│   │   ├── ollama_service.py      ← Comunicación con Ollama
│   │   ├── roles_service.py       ← Definición de roles y prompts
│   │   └── historial_service.py   ← Gestión del historial JSON
│   ├── models/
│   │   └── schemas.py             ← Modelos Pydantic (validación)
│   └── data/                      ← Creado automáticamente
│       ├── historiales/           ← Conversaciones guardadas en JSON
│       └── contextos/             ← Contextos de negocio en JSON
├── frontend/
│   └── index.html                 ← App web completa (sin build)
├── whatsapp-bot/
│   ├── bot.js                     ← Bot de WhatsApp con whatsapp-web.js
│   ├── package.json               ← Dependencias Node.js
│   └── node_modules/              ← (NO se sube a GitHub)
├── .gitignore
├── INICIAR.bat                    ← Script de inicio rápido (Windows)
└── README.md
```

---

## ⚙️ Requisitos previos

| Herramienta | Versión | Descarga |
|-------------|---------|---------|
| Python | **3.11** (no usar 3.14) | [python.org](https://python.org/downloads) |
| Node.js | 18 LTS o superior | [nodejs.org](https://nodejs.org) |
| Git + Git Bash | 2.x | [git-scm.com](https://git-scm.com/downloads) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| RAM | 8 GB mínimo | 16 GB recomendado para llama3 |

> ⚠️ **Importante:** Usar Python **3.11** específicamente. Python 3.14 tiene incompatibilidades con `python-telegram-bot`.

---

## 🚀 Instalación paso a paso

### 1. Instalar y configurar Ollama

```bash
# Descargar desde https://ollama.com e instalar

# Descargar el modelo LLaMA 3 (4.7 GB)
ollama pull llama3

# Alternativa más ligera (2.7 GB)
ollama pull gemma2:2b

# Verificar modelos instalados
ollama list
```

> ✅ Si Ollama ya está corriendo y aparece el error `bind: Only one usage of each socket address`, **no es un problema** — significa que el servicio ya está activo.

---

### 2. Configurar el Backend

```bash
# Entrar a la carpeta backend
cd CHATBOT/backend

# Crear entorno virtual con Python 3.11
py -3.11 -m venv venv

# Activar el entorno virtual (hacerlo en cada terminal nueva)
source venv/Scripts/activate
# El prompt debe mostrar: (venv) ...

# Instalar dependencias
pip install -r requirements.txt

# Crear el archivo .env con las credenciales
echo "TELEGRAM_TOKEN=tu_token_de_botfather_aqui" > .env
echo "API_URL=http://localhost:8000/api" >> .env

# Iniciar el servidor
uvicorn main:app --reload --port 8000
```

Respuesta esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Verificar en el navegador: http://localhost:8000/api/health

---

### 3. Configurar el Frontend

```bash
# En una nueva terminal:
cd CHATBOT/frontend
python -m http.server 3000
```

Abrir en el navegador: **http://localhost:3000**

---

### 4. Configurar el Bot de Telegram

**Paso 1 — Crear el bot:**
1. Abrir Telegram y buscar `@BotFather`
2. Enviar `/newbot`
3. Seguir las instrucciones y copiar el **TOKEN**

**Paso 2 — Instalar e iniciar:**
```bash
cd CHATBOT/backend
source venv/Scripts/activate
pip install python-telegram-bot==21.5
python telegram_bot.py
```

Respuesta esperada:
```
Bot de Telegram activo. Ctrl+C para detener.
```

**Comandos del bot:**
| Comando | Acción |
|---------|--------|
| `/start` | Bienvenida y rol activo |
| `/rol` | Menú de selección de roles (responder 1-5) |
| `/nuevo` | Nueva conversación |
| Cualquier texto | Pregunta al LLM con el rol activo |

---

### 5. Configurar el Bot de WhatsApp

```bash
# Crear la carpeta e instalar dependencias
cd CHATBOT/whatsapp-bot
npm install

# Iniciar el bot (con FastAPI corriendo)
node bot.js
```

Aparecerá un **código QR** en la terminal. Para escanearlo:
1. Abrir WhatsApp en el celular
2. Ir a **⋮ → Dispositivos vinculados → Vincular dispositivo**
3. Escanear el QR de la terminal

> ⚠️ La sesión se guarda en `.wwebjs_auth/`. Si cambias de computadora o clonas el repositorio, debes escanear el QR nuevamente.

**Comandos del bot:**
| Comando | Acción |
|---------|--------|
| `/start` o `/ayuda` | Bienvenida y menú |
| `/rol` | Selección de rol (responder 1-5) |
| `/nuevo` | Nueva conversación |
| Cualquier texto | Pregunta al LLM |

---

## ▶️ Inicio rápido (sistema completo)

Abrir **4 terminales** en este orden:

```bash
# Terminal 1 — FastAPI (PRIMERO)
cd CHATBOT/backend && source venv/Scripts/activate && uvicorn main:app --reload --port 8000

# Terminal 2 — Bot Telegram
cd CHATBOT/backend && source venv/Scripts/activate && python telegram_bot.py

# Terminal 3 — Frontend web
cd CHATBOT/frontend && python -m http.server 3000

# Terminal 4 — Bot WhatsApp
cd CHATBOT/whatsapp-bot && node bot.js
```

O hacer doble clic en **`INICIAR.bat`** para abrir todo automáticamente.

---

## 🌐 API REST — Endpoints disponibles

Con el servidor corriendo, explorar la documentación interactiva en:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Ejemplos de uso con curl

```bash
# Health check
curl http://localhost:8000/api/health

# Listar roles
curl http://localhost:8000/api/roles

# Chat con el Profesor
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Qué es la recursividad?", "rol_id": "profesor", "modelo": "llama3"}'

# Chat con el Programador
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Crea una API REST en Python", "rol_id": "programador", "modelo": "llama3"}'

# Agente de empresa con contexto del negocio
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el horario de atención?",
    "rol_id": "agente_empresa",
    "modelo": "llama3",
    "contexto_adicional": "Somos TechGT. Horario: Lun-Vie 9am-6pm. WhatsApp: +502 5555-0000"
  }'
```

---

## 🔧 Errores frecuentes y soluciones

| Error | Causa | Solución |
|-------|-------|---------|
| `uvicorn: command not found` | venv no activado | `source venv/Scripts/activate` |
| `Could not import module 'main'` | Ejecutar desde carpeta incorrecta | `cd backend` antes de uvicorn |
| `Connection refused :11434` | Ollama no corre | `ollama serve` |
| `Connection refused :8000` | FastAPI no corre | Iniciar uvicorn en Terminal 1 |
| `Model not found` | Modelo no descargado | `ollama pull llama3` |
| `Failed to fetch` (frontend) | FastAPI apagado | Verificar Terminal 1 |
| `RuntimeError: event loop already running` | Conflicto asyncio | Usar `run_polling()` sin `asyncio.run()` |
| `TypeError` con Python 3.14 + Telegram | Incompatibilidad de versión | Crear venv con `py -3.11 -m venv venv` |
| `Execution context destroyed` (WhatsApp) | Sesión corrupta | `rm -rf .wwebjs_auth/` y re-escanear QR |
| Rama `master` en lugar de `main` | Configuración Git antigua | `git config --global init.defaultBranch main` |

---

## 🔒 Archivos que NO se suben a GitHub

```
venv/                        ← Entorno virtual Python (200MB+)
.env                         ← Tokens secretos de Telegram
whatsapp-bot/.wwebjs_auth/   ← Sesión personal de WhatsApp
whatsapp-bot/.wwebjs_cache/  ← Caché temporal
whatsapp-bot/node_modules/   ← Dependencias Node (150MB+)
backend/data/historiales/    ← Conversaciones privadas
backend/data/contextos/      ← Contextos de negocio
```

Al clonar el proyecto en una nueva máquina, recrear:
```bash
# Python
py -3.11 -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt

# Crear .env manualmente con el token de Telegram
echo "TELEGRAM_TOKEN=tu_token" > backend/.env
echo "API_URL=http://localhost:8000/api" >> backend/.env

# Node.js
cd whatsapp-bot && npm install
# Luego escanear el QR de WhatsApp nuevamente
```

---

## 📈 Stack tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| LLM local | Ollama + LLaMA 3 | Motor de inteligencia artificial |
| Backend | FastAPI + Python 3.11 | API REST, lógica de roles e historial |
| Frontend | HTML5 + CSS3 + JS | Interfaz web sin build |
| Bot Telegram | python-telegram-bot 21.5 | Canal de mensajería Telegram |
| Bot WhatsApp | whatsapp-web.js + Node.js | Canal de mensajería WhatsApp |
| Persistencia | JSON local | Historial y contextos sin BD externa |
| Control de versiones | Git + GitHub | Repositorio: github.com/TagoSMD/IA |

---

## 🚀 Mejoras futuras

- [ ] Autenticación de usuarios con JWT
- [ ] Streaming de respuestas (efecto "typing" en tiempo real)
- [ ] RAG — búsqueda en documentos PDF del negocio
- [ ] Despliegue en VPS con Nginx para acceso remoto
- [ ] App móvil nativa con Capacitor (iOS y Android)
- [ ] Panel de administración para gestionar contextos y roles

---

## 📄 Licencia

Proyecto de código abierto para fines educativos.  
Desarrollado con ❤️ en Guatemala — Abril 2026.
