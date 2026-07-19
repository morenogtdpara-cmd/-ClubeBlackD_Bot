from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN, ADMIN_ID
from database import init_db


def painel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚧 Em construção", callback_data="nada")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bot privado.")
        return

    await update.message.reply_text(
        "✅ Bot iniciado."
    )


async def painel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "🎛️ PAINEL",
        reply_markup=painel_keyboard()
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "nada":
        await query.answer(
            "🚧 Ainda não implementado.",
            show_alert=True
        )


def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("painel", painel))

    app.add_handler(
        CallbackQueryHandler(callbacks)
    )

    print("BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()