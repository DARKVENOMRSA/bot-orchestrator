import os
import psutil

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== ENV =====

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set in Railway variables")

# ===== BASIC COMMANDS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Hosting Panel Online\n\n"
        "/ping - Test bot\n"
        "/status - CPU/RAM usage\n"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong — Panel Alive")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    await update.message.reply_text(
        f"📊 Server Status\n\n"
        f"CPU: {cpu}%\n"
        f"RAM: {ram}%"
    )


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Upload system ready (hosting module coming next)")


# ===== BOT START =====

def start_bot_panel():

    print("⚡ Starting Telegram Control Panel")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.Document.ALL, upload))

    print("✅ Control Panel Online")

    app.run_polling(drop_pending_updates=True)        await update.message.reply_text("No bots registered")
        return

    msg = ""
    for b in data:
        msg += f"{b[0]} → {b[1]}\n"

    await update.message.reply_text(msg)


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /run bot.py")

    name = context.args[0]

    ok = start_bot(name, f"{BOT_FOLDER}/{name}")

    await update.message.reply_text("Started ✅" if ok else "Failed ❌")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /stop bot.py")

    name = context.args[0]

    ok = stop_bot(name)

    await update.message.reply_text("Stopped ✅" if ok else "Failed ❌")


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    doc = update.message.document

    if not doc:
        return

    name = doc.file_name

    if not name.endswith((".py", ".js")):
        return await update.message.reply_text("Only .py or .js allowed")

    file = await doc.get_file()
    path = f"{BOT_FOLDER}/{name}"

    await file.download_to_drive(path)

    add_bot(name, path)

    await update.message.reply_text(f"✅ Registered: {name}")


def start_bot_panel():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bots", bots))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.Document.ALL, upload))

    print("🚀 Control Panel Online")

    app.run_polling()
