from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import painel_keyboard, vip_keyboard, album_keyboard


AGUARDANDO_DIVULGACAO = set()

AGUARDANDO_ALBUM = {}


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
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

    if update.effective_user.id != ADMIN_ID:
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

        AGUARDANDO_DIVULGACAO.add(
            query.from_user.id
        )

        await query.message.reply_text(
            "📢 MODO DIVULGAÇÃO ATIVADO\n\n"
            "📤 Envie sua publicação.\n\n"
            "Aceito:\n"
            "✅ Texto\n"
            "✅ Foto\n"
            "✅ Vídeo\n"
            "✅ Áudio"
        )

        return


    elif query.data == "album":

        await query.message.reply_text(
            "🖼️ CENTRAL DE ÁLBUM\n\n"
            "Escolha uma opção:",
            reply_markup=album_keyboard()
        )

        return


    elif query.data == "album_agora":

        AGUARDANDO_ALBUM[query.from_user.id] = []

        await query.message.reply_text(
            "🖼️ MODO ÁLBUM ATIVADO\n\n"
            "📤 Envie as fotos ou vídeos.\n\n"
            "📌 Limite máximo: 10 mídias."
        )

        return


    elif query.data == "finalizar_album":

        await query.message.reply_text(
            "✅ Álbum finalizado. Preparando envio..."
        )

        return


    else:

        await query.message.reply_text(
            "Opção em construção."
        )


async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in AGUARDANDO_ALBUM:
        return


    if update.message.photo:

        AGUARDANDO_ALBUM[user_id].append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id
            }
        )


    elif update.message.video:

        AGUARDANDO_ALBUM[user_id].append(
            {
                "tipo": "video",
                "id": update.message.video.file_id
            }
        )

    else:
        return


    if len(AGUARDANDO_ALBUM[user_id]) > 10:

        AGUARDANDO_ALBUM[user_id].pop()

        await update.message.reply_text(
            "⚠️ Limite máximo de 10 mídias atingido."
        )

        return


    finalizar = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ FINALIZAR ÁLBUM",
                callback_data="finalizar_album"
            )
        ]
    ])


    await update.message.reply_text(
        "PARA O ENVIO APERTE EM FINALIZAR",
        reply_markup=finalizar
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
        return


    AGUARDANDO_DIVULGACAO.remove(
        user_id
    )


    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )