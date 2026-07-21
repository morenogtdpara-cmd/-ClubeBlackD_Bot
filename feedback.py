from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import vip_keyboard


FEEDBACK = 2


LEGENDA_FEEDBACK = """
⭐ FEEDBACK REAL ⭐️

Mais um cliente satisfeito.

Quer ter acesso ao conteúdo completo?

💦 Faça parte você também.
"""


async def abrir_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return ConversationHandler.END

    await query.message.reply_text(
        "⭐ FEEDBACK ATIVADO\n\n"
        "📸 Envie a foto."
    )

    return FEEDBACK


async def receber_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message.photo:
        return FEEDBACK

    await context.bot.send_photo(
        chat_id=GROUP_ID,
        photo=update.message.photo[-1].file_id,
        caption=LEGENDA_FEEDBACK,
        reply_markup=vip_keyboard(VIP_LINK)
    )

    await update.message.reply_text(
        "✅ Feedback enviado."
    )

    return ConversationHandler.END