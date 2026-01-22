import os
import json
import psutil
import asyncio
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

BASE_DIR = os.getcwd()
BOTS_DIR = os.path.join(BASE_DIR, "bots")
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

REGISTRY_FILE = os.path.join(DATA_DIR, "bots.json")

MAX_BOTS = 10

os.makedirs(BOTS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

RUNNING = {}

# ---------------------------
# STORAGE
# ---------------------------

def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)

def save_registry(data):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f)

# ---------------------------
# CORE
# ---------------------------

def launch_bot(name):
    path = os.path.join(BOTS_DIR, name)
    log_path = os.path.join(LOG_DIR, f"{name}.log")

    log_file = open(log_path, "a")

    proc = subprocess.Popen(
        ["python", path],
        stdout=log_file,
        stderr=log_file
    )

    RUNNING[name] = proc

    registry = load_registry()
    registry[name] = {"running": True}
    save_registry(registry)

def stop_bot_proc(name):
    if name in RUNNING:
        RUNNING[name].kill()
        del RUNNING[name]

    registry = load_registry()
    if name in registry:
        registry[name]["running"] = False
        save_registry(registry)

# ---------------------------
# AUTO RESTORE
# ---------------------------

def restore_bots():
    registry = load_registry()

    for name, info in registry.items():
        if info.get("running"):
            if len(RUNNING) < MAX_BOTS:
                launch_bot(name)

# ---------------------------
# COMMANDS
# ---------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Hosting Panel Online\n\n"
        "/upload\n"
        "/list\n"
        "/stats\n"
        "/logs bot.py\n\n"
        "Use buttons to manage bots."
    )

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc:
        return

    path = os.path.join(BOTS_DIR, doc.file_name)
    file = await doc.get_file()
    await file.download_to_drive(path)

    await update.message.reply_text(f"✅ Uploaded {doc.file_name}")

async def list_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = os.listdir(BOTS_DIR)

    if not files:
        await update.message.reply_text("📂 No bots uploaded")
        return

    buttons = []

    for f in files:
        buttons.append([
            InlineKeyboardButton(f"▶ {f}", callback_data=f"start|{f}"),
            InlineKeyboardButton(f"⏹ {f}", callback_data=f"stop|{f}")
        ])

    await update.message.reply_text(
        "📦 Your bots:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent

    msg = (
        f"📊 System Stats\n\n"
        f"CPU: {cpu}%\n"
        f"RAM: {mem}%\n"
        f"Running Bots: {len(RUNNING)}/{MAX_BOTS}"
    )

    await update.message.reply_text(msg)

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /logs bot.py")
        return

    name = context.args[0]
    log_file = os.path.join(LOG_DIR, f"{name}.log")

    if not os.path.exists(log_file):
        await update.message.reply_text("❌ No logs found")
        return

    with open(log_file, "r") as f:
        data = f.read()[-3500:]

    await update.message.reply_text(f"📜 Logs for {name}:\n\n{data}")

# ---------------------------
# BUTTON HANDLER
# ---------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, name = query.data.split("|")

    if action == "start":
        if len(RUNNING) >= MAX_BOTS:
            await query.edit_message_text("⚠ Bot limit reached")
            return

        launch_bot(name)
        await query.edit_message_text(f"▶ Started {name}")

    elif action == "stop":
        stop_bot_proc(name)
        await query.edit_message_text(f"⏹ Stopped {name}")

# ---------------------------
# START PANEL
# ---------------------------

def start_panel():
    print("⚡ Hosting Engine Online")

    restore_bots()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(False)
        .build()
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.bot.delete_webhook(drop_pending_updates=True))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("list", list_bots))
    app.add_handler(CommandHandler("logs", logs))

    app.add_handler(MessageHandler(filters.Document.ALL, upload_file))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Panel Ready")

    app.run_polling(drop_pending_updates=True)
