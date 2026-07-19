from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import painel_keyboard, vip_keyboard, album_keyboard


AGUARDANDO_ALBUM = 1


AGUARDANDO_DIVULGACAO = set()
ALBUM_MIDIAS = {}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bot privado.")
        return

    await update.message.reply_text("✅ Bot iniciado.")



async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚡️ PAINEL DE COMANDOS\n\nEscolha uma opção:",
        reply_markup=painel_keyboard()
    )



async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()


    if query.data == "divulgar":

        AGUARDANDO_DIVULGACAO.add(query.from_user.id)

        await query.message.reply_text(
            "📢 MODO DIVULGAÇÃO ATIVADO\n\n"
            "📤 Envie sua publicação."
        )

        return



    if query.data == "album":

        await query.message.reply_text(
            "🖼️ CENTRAL DE ÁLBUM\n\nEscolha uma opção:",
            reply_markup=album_keyboard()
        )

        return



    if query.data == "album_agora":

        ALBUM_MIDIAS[query.from_user.id] = []

        await query.message.reply_text(
            "🖼️ MODO ÁLBUM ATIVADO\n\n"
            "📤 Envie as fotos ou vídeos."
        )

        return AGUARDANDO_ALBUM



async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id


    if user_id not in ALBUM_MIDIAS:
        ALBUM_MIDIAS[user_id] = []


    if update.message.photo:

        ALBUM_MIDIAS[user_id].append(
            update.message.photo[-1].file_id
        )


    elif update.message.video:

        ALBUM_MIDIAS[user_id].append(
            update.message.video.file_id
        )


    await update.message.reply_text(
        f"✅ Mídia adicionada ({len(ALBUM_MIDIAS[user_id])})\n\n"
        "Envie mais ou finalize."
    )


    return AGUARDANDO_ALBUM



async def finalizar_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id


    await query.message.reply_text(
        "✅ Álbum finalizado."
    )


    ALBUM_MIDIAS.pop(
        user_id,
        None
    )


    return ConversationHandler.END