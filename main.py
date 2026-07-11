import os
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1004231485932
OWNER_ID = 8880948641


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "✅ Bot está online!\n\n"
        "Envie uma postagem e responda com /divulgar para publicar."
    )


async def divulgar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ Responda a mensagem que deseja divulgar usando /divulgar."
        )
        return

    mensagem = update.message.reply_to_message

    await context.bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=mensagem.chat.id,
        message_id=mensagem.message_id
    )

    await update.message.reply_text(
        "✅ Divulgação feita com sucesso!"
    )


async def configurar_menu(app):
    comandos = [
        BotCommand("start", "Ver se o bot está online"),
        BotCommand("divulgar", "Divulgar postagem no grupo")
    ]

    await app.bot.set_my_commands(comandos)


app = Application.builder().token(BOT_TOKEN).post_init(configurar_menu).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("divulgar", divulgar))

print("Bot iniciado")

app.run_polling()