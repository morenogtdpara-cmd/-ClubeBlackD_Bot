from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN, ADMIN_ID
from database import init_db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bot privado.")
        return

    await update.message.reply_text(
        "✅ Bot iniciado."
    )


async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚙️ BLACK MANAGER\n\n🚧 Sistema em construção."
    )


def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manager", manager))

    print("BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()