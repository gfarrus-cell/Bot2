
import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# CONFIGURACIÓN PRINCIPAL
TOKEN = os.getenv("token")  # Token desde variables de entorno
CHAT_ID = None  # Se completará al primer mensaje

# Horarios de recordatorio (hora local)
HORARIOS = ["08:00", "13:00", "18:00", "21:00"]

# Lista de suplementos
SUPLEMENTOS = {
    "08:00": "Vitamina D3 y Omega 3",
    "13:00": "Zinc + Vitamina B6",
    "18:00": "Proteína Whey (post entrenamiento)",
    "21:00": "Magnesio (citrato/glicinato)"
}

# Base de datos simple en memoria
registro = {}

# Zona horaria Argentina
timezone = pytz.timezone("America/Argentina/Buenos_Aires")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text("¡Hola! Soy tu bot de salud. Te recordaré tomar tus suplementos en los horarios establecidos.")

# Mensajes de confirmación
async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip().lower()
    hoy = datetime.date.today().isoformat()
    if hoy not in registro:
        registro[hoy] = []

    if user_msg in ["listo", "hecho", "ok", "tomado"]:
        registro[hoy].append(datetime.datetime.now(timezone).strftime("%H:%M"))
        await update.message.reply_text("✅ Registrado. ¡Buen trabajo!")
    else:
        await update.message.reply_text("No entendí. Escribí 'Listo' cuando tomes tu suplemento.")

# Tareas automáticas de recordatorio
async def enviar_recordatorio(context: ContextTypes.DEFAULT_TYPE):
    ahora = datetime.datetime.now(timezone).strftime("%H:%M")
    if ahora in SUPLEMENTOS and CHAT_ID is not None:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"⏰ {ahora} - ¡Hora de tomar: {SUPLEMENTOS[ahora]}! Responde 'Listo' cuando lo hagas.")

# Configuración principal
app = ApplicationBuilder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))

# Tareas programadas
for horario in HORARIOS:
    h, m = map(int, horario.split(":"))
    app.job_queue.run_daily(enviar_recordatorio, time=datetime.time(h, m, tzinfo=timezone))

print("Bot en ejecución... Usa /start en Telegram para iniciar.")
app.run_polling()
