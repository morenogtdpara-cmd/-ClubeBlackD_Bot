from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import vip_keyboard


AGUARDANDO_FEEDBACK = set()


LEGENDA_FEEDBACK = """
🔥 FEEDBACK VIP 🔥

Sua legenda fixa aqui.
"""


async def abrir_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    AGUARDANDO_FEEDBACK.add(
        query.from_user.id
    )

    await query.message.reply_text(
        "⭐ FEEDBACK ATIVADO\n\n"
        "📸 Envie a foto."
    )


async def receber_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in AGUARDANDO_FEEDBACK:
        return

    if not update.message.photo:
        return

    await context.bot.send_photo(
        chat_id=GROUP_ID,
        photo=update.message.photo[-1].file_id,
        caption=LEGENDA_FEEDBACK,
        reply_markup=vip_keyboard(VIP_LINK)
    )

    AGUARDANDO_FEEDBACK.remove(
        user_id
    )

    await update.message.reply_text(
        "✅ Feedback enviado."
    )
