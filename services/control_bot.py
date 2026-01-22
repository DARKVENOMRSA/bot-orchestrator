from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID


app = Application.builder().token(BOT_TOKEN).build()


def is_owner(uid):
    return uid == OWNER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only")
        return

    keyboard = [
        [InlineKeyboardButton("📂 Files", callback_data="files")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("▶ Start", callback_data="start")],
        [InlineKeyboardButton("⏹ Stop", callback_data="stop")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
    ]

    await update.message.reply_text(
        "🔥 *FluxHost Control Panel*\n\nSelect option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        await query.edit_message_text("❌ Owner only")
        return

    data = query.data

    if data == "files":
        await query.edit_message_text("📂 No files yet")

    elif data == "stats":
        await query.edit_message_text(
            "📊 System Stats\n\nCPU: OK\nRAM: OK\nBots: 1/10"
        )

    elif data == "start":
        await query.edit_message_text("▶ Bots started")

    elif data == "stop":
        await query.edit_message_text("⏹ Bots stopped")

    elif data == "settings":
        await query.edit_message_text("⚙ Settings coming soon")


app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))


def get_bot_app():
    return app
