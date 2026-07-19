from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import vip_keyboard


AGUARDANDO_DIVULGACAO = set()


async def iniciar_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    AGUARDANDO_DIVULGACAO.add(user_id)

    await update.message.reply_text(
        "📤 Envie a publicação.\n\n"
        "Aceito:\n"
        "✅ Texto\n"
        "✅ Foto\n"
        "✅ Vídeo\n"
        "✅ Áudio"
    )


async def receber_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in AGUARDANDO_DIVULGACAO:
        return

    if update.message.photo:

        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=update.message.caption,
            reply_markup=vip_keyboard(VIP_LINK)
        )

    elif update.message.video:

        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=update.message.caption,
            reply_markup=vip_keyboard(VIP_LINK)
        )

    elif update.message.audio:

        await context.bot.send_audio(
            chat_id=GROUP_ID,
            audio=update.message.audio.file_id,
            caption=update.message.caption,
            reply_markup=vip_keyboard(VIP_LINK)
        )

    elif update.message.text:

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=update.message.text,
            reply_markup=vip_keyboard(VIP_LINK)
        )

    else:

        await update.message.reply_text(
            "⚠️ Tipo de mensagem não permitido."
        )
        return


    AGUARDANDO_DIVULGACAO.remove(user_id)

    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )
    async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "divulgar":

        await query.message.reply_text(
            "📢 CENTRAL DE DIVULGAÇÃO\n\n"
            "Clique para enviar sua publicação."
        )

        await iniciar_divulgacao(
            query.message,
            context
        )