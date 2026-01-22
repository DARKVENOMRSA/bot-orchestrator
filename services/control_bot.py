import os
import subprocess
import json
import asyncio
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

BOTS_FOLDER = "bots"
DATA_FILE = "data/running.json"

os.makedirs(BOTS_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

running_bots = {}
task_queue = asyncio.Queue()


# ---------------- STORAGE ---------------- #

def save_state():
    with open(DATA_FILE, "w") as f:
        json.dump(list(running_bots.keys()), f)


def load_state():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------- BOT CONTROL ---------------- #

async def start_bot(name):
    if name in running_bots:
        return "Already running"

    path = f"{BOTS_FOLDER}/{name}"

    if not os.path.exists(path):
        return "File not found"

    process = subprocess.Popen(
        ["python", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    running_bots[name] = process
    save_state()

    asyncio.create_task(watchdog(name))

    return "Started"


async def stop_bot(name):
    if name not in running_bots:
        return "Not running"

    running_bots[name].terminate()
    del running_bots[name]
    save_state()

    return "Stopped"


async def restart_bot(name):
    await stop_bot(name)
    await asyncio.sleep(1)
    return await start_bot(name)


# ---------------- WATCHDOG ---------------- #

async def watchdog(name):
    proc = running_bots.get(name)

    if not proc:
        return

    await asyncio.to_thread(proc.wait)

    if name in running_bots:
        del running_bots[name]
        save_state()
        await start_bot(name)


# ---------------- COMMANDS ---------------- #

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ Panel Online\n\n"
        "/upload — send bot file\n"
        "/list — running bots\n"
        "/panel — control panel"
    )


async def list_cmd(update: Update, context):
    if not running_bots:
        await update.message.reply_text("No bots running")
        return

    txt = "\n".join(running_bots.keys())
    await update.message.reply_text(f"Running:\n{txt}")


# ---------------- FILE UPLOAD ---------------- #

async def upload_bot(update: Update, context):
    doc = update.message.document

    if not doc.file_name.endswith(".py"):
        await update.message.reply_text("Only .py files allowed")
        return

    file = await doc.get_file()
    path = f"{BOTS_FOLDER}/{doc.file_name}"

    await file.download_to_drive(path)

    await update.message.reply_text(f"Uploaded {doc.file_name}")


# ---------------- PANEL ---------------- #

async def panel_cmd(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("▶ Start", callback_data="start")],
        [InlineKeyboardButton("⏹ Stop", callback_data="stop")],
        [InlineKeyboardButton("♻ Restart", callback_data="restart")],
        [InlineKeyboardButton("📊 Logs", callback_data="logs")]
    ]

    await update.message.reply_text(
        "Bot Control Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def panel_buttons(update: Update, context):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Send bot filename")


# ---------------- LOG VIEWER ---------------- #

async def logs_cmd(update: Update, context):
    if not context.args:
        await update.message.reply_text("/logs bot.py")
        return

    name = context.args[0]

    if name not in running_bots:
        await update.message.reply_text("Bot not running")
        return

    proc = running_bots[name]

    output = proc.stdout.readline().decode()

    if not output:
        output = "No logs yet"

    await update.message.reply_text(output)


# ---------------- QUEUE SYSTEM ---------------- #

async def queue_worker():
    while True:
        name, action = await task_queue.get()

        if action == "start":
            await start_bot(name)

        elif action == "stop":
            await stop_bot(name)

        elif action == "restart":
            await restart_bot(name)

        task_queue.task_done()


# ---------------- RESTORE ---------------- #

async def restore_bots():
    old = load_state()

    for bot in old:
        await start_bot(bot)


# ---------------- BOOT ---------------- #

def start_bot_panel():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("panel", panel_cmd))
    app.add_handler(CommandHandler("logs", logs_cmd))

    app.add_handler(MessageHandler(filters.Document.ALL, upload_bot))
    app.add_handler(CallbackQueryHandler(panel_buttons))

    loop = asyncio.get_event_loop()
    loop.create_task(queue_worker())
    loop.create_task(restore_bots())

    print("⚡ Hosting Engine Online")

    app.run_polling(drop_pending_updates=True)
