from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
)

from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import painel_keyboard, vip_keyboard, album_keyboard

ALBUM = 1

AGUARDANDO_DIVULGACAO = set()
ALBUM_MIDIAS = {}

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

        return ALBUM

async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in ALBUM_MIDIAS:
        ALBUM_MIDIAS[user_id] = []

    if update.message.photo:

        ALBUM_MIDIAS[user_id].append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id
            }
        )

    elif update.message.video:

        ALBUM_MIDIAS[user_id].append(
            {
                "tipo": "video",
                "id": update.message.video.file_id
            }
        )

    finalizar = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ FINALIZAR ÁLBUM",
                callback_data="finalizar_album"
            )
        ]
    ])

    await update.message.reply_text(
        f"✅ Mídia adicionada ({len(ALBUM_MIDIAS[user_id])})",
        reply_markup=finalizar
    )

    return ALBUM

async def finalizar_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    midias = ALBUM_MIDIAS.get(
        user_id,
        []
    )

    if not midias:

        await query.message.reply_text(
            "⚠️ Nenhuma mídia no álbum."
        )

        return ConversationHandler.END

    lista_envio = []

    for item in midias:

        if item["tipo"] == "foto":

            lista_envio.append(
                InputMediaPhoto(
                    media=item["id"]
                )
            )

        elif item["tipo"] == "video":

            lista_envio.append(
                InputMediaVideo(
                    media=item["id"]
                )
            )

    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=lista_envio
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🔥 Entre no VIP:",
        reply_markup=vip_keyboard(VIP_LINK)
    )
     adicionar_envio(1)

    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )
    await query.message.reply_text(
        "✅ Álbum enviado com sucesso."
    )

    ALBUM_MIDIAS.pop(
        user_id,
        None
    )

    return ConversationHandler.END

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
from database import adicionar_envio
    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )