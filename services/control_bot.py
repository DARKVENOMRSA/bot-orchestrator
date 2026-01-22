import os
import threading
import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from core.db import init_db
from core.runner import (
    register_bot,
    list_bots,
    start_bot,
    stop_bot,
    watchdog,
    restore_bots
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

BOT_DIR = "bots"
os.makedirs(BOT_DIR, exist_ok=True)

MAX_BOTS = 10


# ===== TELEGRAM COMMANDS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hosting Panel Online\n\n"
        "/bots\n"
        "/run bot.py\n"
        "/stop bot.py\n"
        "Upload .py or .js"
    )


async def bots(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = list_bots()

    if not data:
        return await update.message.reply_text("No bots registered")

    msg = ""
    for b in data:
        msg += f"{b[0]} → {b[1]}\n"

    await update.message.reply_text(msg)


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return await update.message.reply_text("Usage: /run bot.py")

    name = context.args[0]
    path = f"{BOT_DIR}/{name}"

    ok, msg = start_bot(name, path)

    await update.message.reply_text(msg)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return await update.message.reply_text("Usage: /stop bot.py")

    name = context.args[0]

    ok, msg = stop_bot(name)

    await update.message.reply_text(msg)


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    doc = update.message.document

    if not doc:
        return

    name = doc.file_name

    if not name.endswith((".py", ".js")):
        return await update.message.reply_text("Only .py or .js allowed")

    if len(list_bots()) >= MAX_BOTS:
        return await update.message.reply_text("Bot limit reached (10)")

    file = await doc.get_file()
    path = f"{BOT_DIR}/{name}"

    await file.download_to_drive(path)

    register_bot(name, path)

    await update.message.reply_text(f"✅ Registered {name}")


# ===== BACKGROUND WATCHDOG THREAD =====

def watchdog_loop():
    while True:
        watchdog()
        time.sleep(5)


# ===== START PANEL =====

def start_bot_panel():

    print("⚡ Booting Hosting Engine")

    init_db()

    # Restore previous running bots
    restore_bots()

    # Start watchdog thread
    t = threading.Thread(target=watchdog_loop, daemon=True)
    t.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bots", bots))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.Document.ALL, upload))

    print("✅ Hosting Engine Online")

    app.run_polling(drop_pending_updates=True)
