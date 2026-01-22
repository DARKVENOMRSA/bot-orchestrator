from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID

app = Application.builder().token(BOT_TOKEN).build()


# ---------- ACCESS CHECK ----------

def is_owner(user_id: int):
    return user_id == OWNER_ID


# ---------- START PANEL ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not is_owner(user.id):
        await update.message.reply_text("❌ Access denied")
        return

    keyboard = [
        [InlineKeyboardButton("📂 Files", callback_data="files")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("▶ Start Bots", callback_data="startbots")],
        [InlineKeyboardButton("⏹ Stop Bots", callback_data="stopbots")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
    ]

    await update.message.reply_text(
        "🔥 *Hosting Control Panel*\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ---------- BUTTON HANDLER ----------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        await query.edit_message_text("❌ Access denied")
        return

    data = query.data

    if data == "files":
        await query.edit_message_text("📂 No files uploaded yet")

    elif data == "stats":
        await query.edit_message_text(
            "📊 *System Stats*\n\nCPU: Normal\nRAM: Normal\nRunning Bots: 1/10",
            parse_mode="Markdown"
        )

    elif data == "startbots":
        await query.edit_message_text("▶ Bots started successfully")

    elif data == "stopbots":
        await query.edit_message_text("⏹ Bots stopped successfully")

    elif data == "settings":
        await query.edit_message_text("⚙ Settings panel (coming soon)")


# ---------- REGISTER ----------

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))


# ---------- EXPORT FOR MAIN ----------

def get_bot_app():
    return app# BUTTON HANDLER
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
