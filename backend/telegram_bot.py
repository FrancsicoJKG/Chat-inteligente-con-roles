import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

sesiones = {}
ROLES_MENU = {
    "1": ("profesor", "Profesor"),
    "2": ("programador", "Programador"),
    "3": ("psicologo", "Psicologo"),
    "4": ("negocios", "Negocios"),
    "5": ("agente_empresa", "Agente Empresa"),
}

def obtener_sesion(chat_id):
    if chat_id not in sesiones:
        sesiones[chat_id] = {"rol": "profesor", "sesion_id": None, "esperando_rol": False}
    return sesiones[chat_id]

def enviar_a_api_sync(chat_id, pregunta):
    import httpx
    s = obtener_sesion(chat_id)
    try:
        r = httpx.post(f"{API_URL}/chat", json={
            "pregunta": pregunta,
            "rol_id": s["rol"],
            "modelo": "llama3",
            "sesion_id": s["sesion_id"],
        }, timeout=120)
        datos = r.json()
        s["sesion_id"] = datos["sesion_id"]
        return datos["respuesta"]
    except Exception as e:
        return f"Error: {str(e)}"

def run_bot():
    import telegram
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram import Update
    import asyncio

    async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        s = obtener_sesion(update.effective_chat.id)
        await update.message.reply_text(
            f"Bienvenido al Chat IA!\nRol actual: {s['rol']}\n\n"
            "/rol - Cambiar rol\n/nuevo - Nueva conversacion\n\nEscribe tu pregunta!"
        )

    async def cmd_rol(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        obtener_sesion(update.effective_chat.id)["esperando_rol"] = True
        await update.message.reply_text(
            "Elige un rol:\n\n1 - Profesor\n2 - Programador\n"
            "3 - Psicologo\n4 - Negocios\n5 - Agente Empresa\n\nResponde con el numero:"
        )

    async def cmd_nuevo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        obtener_sesion(update.effective_chat.id)["sesion_id"] = None
        await update.message.reply_text("Nueva conversacion iniciada.")

    async def mensaje(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        texto = update.message.text
        s = obtener_sesion(chat_id)

        if s["esperando_rol"] and texto in ROLES_MENU:
            rol_id, nombre = ROLES_MENU[texto]
            s["rol"] = rol_id
            s["sesion_id"] = None
            s["esperando_rol"] = False
            await update.message.reply_text(f"Rol cambiado a: {nombre}")
            return

        await ctx.bot.send_chat_action(chat_id=chat_id, action="typing")
        respuesta = enviar_a_api_sync(chat_id, texto)
        for i in range(0, len(respuesta), 4000):
            await update.message.reply_text(respuesta[i:i+4000])

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rol", cmd_rol))
    app.add_handler(CommandHandler("nuevo", cmd_nuevo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje))

    print("Bot de Telegram activo. Ctrl+C para detener.")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
