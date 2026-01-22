import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

BOTS_DIR = "bots"
RUNNING = {}

os.makedirs(BOTS_DIR, exist_ok=True)

# ------------------------
# COMMAND HANDLERS
# ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Hosting Panel Online\n\n"
        "/upload → Send bot file\n"
        "/run filename.py\n"
        "/stop filename.py\n"
        "/list"
    )

async def list_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    files = os.listdir(BOTS_DIR)

    if not files:
        await update.message.reply_text("📂 No bots uploaded")
        return

    msg = "📦 Uploaded Bots:\n\n"
    for f in files:
        msg += f"- {f}\n"

    await update.message.reply_text(msg)

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc:
        return

    file_path = os.path.join(BOTS_DIR, doc.file_name)

    telegram_file = await doc.get_file()
    await telegram_file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ Uploaded: {doc.file_name}")

async def run_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/run filename.py")
        return

    name = context.args[0]
    path = os.path.join(BOTS_DIR, name)

    if not os.path.exists(path):
        await update.message.reply_text("❌ File not found")
        return

    if name in RUNNING:
        await update.message.reply_text("⚠ Bot already running")
        return

    proc = subprocess.Popen(
        ["python", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    RUNNING[name] = proc

    await update.message.reply_text(f"🚀 Started {name}")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/stop filename.py")
        return

    name = context.args[0]

    if name not in RUNNING:
        await update.message.reply_text("❌ Bot not running")
        return

    RUNNING[name].kill()
    del RUNNING[name]

    await update.message.reply_text(f"🛑 Stopped {name}")

# ------------------------
# MAIN START
# ------------------------

def start_bot_panel():
    print("⚡ Hosting Engine Online")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(False)
        .build()
    )

    # Force webhook removal (prevents conflict bug)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.bot.delete_webhook(drop_pending_updates=True))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_bots))
    app.add_handler(CommandHandler("run", run_bot))
    app.add_handler(CommandHandler("stop", stop_bot))

    app.add_handler(MessageHandler(filters.Document.ALL, upload_file))

    print("✅ Panel polling started")

    app.run_polling(drop_pending_updates=True)
