from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID
from services.bot_runner import list_bots, start_bot_process
from services.resource_monitor import get_stats

import os

# ---------------- SECURITY ---------------- #

async def owner_only(update):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ Owner Only Panel")
        return False
    return True

# ---------------- BUTTON UI ---------------- #

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📂 My Bots", callback_data="list")],
        [InlineKeyboardButton("🚀 Start Bot", callback_data="start")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------------- COMMANDS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update):
        return

    await update.message.reply_text(
        "🔥 Hosting Panel Online\n\nUse buttons below:",
        reply_markup=main_menu()
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update):
        return

    cpu, ram, running = get_stats()

    await update.message.reply_text(
        f"📊 System Stats\n\nCPU: {cpu}%\nRAM: {ram}%\nRunning Bots: {running}/10"
    )

# ---------------- BUTTON HANDLER ---------------- #

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.edit_message_text("⛔ Owner Only")
        return

    data = query.data

    if data == "list":
        bots = list_bots()

        if not bots:
            await query.edit_message_text("📂 No bots uploaded yet.")
            return

        msg = "📂 Your Bots:\n\n"
        for b in bots:
            msg += f"▶ {b}\n"

        await query.edit_message_text(msg)

    if data == "start":
        bots = list_bots()

        if not bots:
            await query.edit_message_text("❌ No bots found.")
            return

        start_bot_process(bots[0])
        await query.edit_message_text("✅ Bot started successfully")

    if data == "stats":
        cpu, ram, running = get_stats()
        await query.edit_message_text(
            f"📊 System Stats\n\nCPU: {cpu}%\nRAM: {ram}%\nRunning Bots: {running}/10"
        )

# ---------------- BOOT ---------------- #

def start_bot_panel():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("⚡ Hosting Panel Online")

    app.run_polling(drop_pending_updates=True)
