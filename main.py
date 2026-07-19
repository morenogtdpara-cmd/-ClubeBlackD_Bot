from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
def manager_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🖼️ ÁLBUM",
                callback_data="album"
            ),
            InlineKeyboardButton(
                "📢 DIVULGAR",
                callback_data="divulgar"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ FEEDBACKS",
                callback_data="feedbacks"
            ),
            InlineKeyboardButton(
                "📅 AGENDAMENTOS",
                callback_data="agendamentos"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 ESTATÍSTICA",
                callback_data="estatistica"
            )
        ]
    ])
from config import BOT_TOKEN, ADMIN_ID
from database import init_db


def manager_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 DIVULGAR", callback_data="divulgar"),
            InlineKeyboardButton("🖼️ ÁLBUM", callback_data="album")
        ],
        [
            InlineKeyboardButton("⭐ FEEDBACKS", callback_data="feedbacks"),
            InlineKeyboardButton("📅 AGENDAMENTOS", callback_data="agendamentos")
        ],
        [
            InlineKeyboardButton("📊 RELATÓRIO", callback_data="relatorio")
        ]
    ])

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
    "⚡️ PAINEL DE COMANDOS\n\nEscolha uma opção:",
    reply_markup=manager_keyboard()
)


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "DIVULGAR":
        texto = "📢 Divulgação\n\n🚧 Em construção."

    elif query.data == "album":
        texto = "🖼️ Álbum\n\n🚧 Em construção."

    elif query.data == "feedbacks":
        texto = "⭐ Feedbacks\n\n🚧 Em construção."

    elif query.data == "agendamentos":
        texto = "📅 Agendamentos\n\n🚧 Em construção."

    elif query.data == "status":
        texto = "📊 Status do bot\n\n✅ Online."

    else:
        texto = "Opção inválida."


    await query.message.reply_text(texto)


def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manager", manager))

    app.add_handler(
        CallbackQueryHandler(callbacks)
    )

    print("BOT ONLINE")

    app.run_polling()


if __name__ == "__main__":
    main()