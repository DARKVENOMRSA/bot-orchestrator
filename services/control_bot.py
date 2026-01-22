from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

from core.registry import add_bot, list_bots
from core.runner import start_bot, stop_bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

BOT_FOLDER = "bots"
os.makedirs(BOT_FOLDER, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "🤖 Bot Orchestrator Panel\n\n"
        "/bots - list bots\n"
        "/run bot.py\n"
        "/stop bot.py\n"
        "Upload .py or .js files"
    )


async def bots(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    data = list_bots()

    if not data:
        await update.message.reply_text("No bots registered")
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
