from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID
from keyboards import painel_keyboard


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "Bot privado."
        )
        return

    await update.message.reply_text(
        "✅ Bot iniciado."
    )


async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚡️ PAINEL DE COMANDOS\n\nEscolha uma opção:",
        reply_markup=painel_keyboard()
    )


async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "divulgar":

        await query.message.reply_text(
            "📢 Central de divulgação."
        )

    elif query.data == "album":

        await query.message.reply_text(
            "🖼️ Central de álbum."
        )

    elif query.data == "feedbacks":

        await query.message.reply_text(
            "⭐ Feedbacks em construção."
        )

    elif query.data == "relatorio":

        await query.message.reply_text(
            "📊 Relatório em construção."
        )

    elif query.data == "fila":

        await query.message.reply_text(
            "⏰ Fila vazia."
        )