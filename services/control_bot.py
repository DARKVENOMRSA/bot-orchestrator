from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BOT_TOKEN, OWNER_ID, WEBHOOK_URL
import os

# -------------------------
# START COMMAND
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access denied")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("⚡ Restart", callback_data="restart")],
        [InlineKeyboardButton("🧠 System Info", callback_data="sysinfo")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✅ Hosting Panel Online\n\nSelect an option:",
        reply_markup=reply_markup
    )


# -------------------------
# BUTTON HANDLER
# -------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "status":
        await query.edit_message_text("🟢 Panel Status: ONLINE")

    elif data == "restart":
        await query.edit_message_text("♻ Restart requested (demo mode)")

    elif data == "sysinfo":
        text = (
            "🧠 System Info\n\n"
            "CPU: Railway Container\n"
            "RAM: Dynamic\n"
            "Mode: Webhook\n"
            "Bots: Core Panel"
        )
        await query.edit_message_text(text)


# -------------------------
# START WEBHOOK SERVER
# -------------------------

def start_panel():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing")

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    PORT = int(os.environ.get("PORT", 8080))

    print("⚡ Hosting Engine Online")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )
