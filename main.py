import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1004231485932

async def enviar_para_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id:
        await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.VIDEO | filters.PHOTO | filters.TEXT,
        enviar_para_grupo
    )
)

print("Bot iniciado")
app.run_polling()