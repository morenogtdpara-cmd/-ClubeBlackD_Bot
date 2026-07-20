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
from database import adicionar_envio, adicionar_album, pegar_relatorio

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


    relatorio = pegar_relatorio()

    envios, midias, albuns, agendados = relatorio


    🥷🏾 𝐁𝐋𝐀𝐂𝐊 𝐏𝐑𝐈𝐕𝐀𝐓𝐄

👑 𝐁𝐞𝐦-𝐯𝐢𝐧𝐝𝐨 𝐝𝐞 𝐯𝐨𝐥𝐭𝐚, 𝐂𝐡𝐞𝐟𝐞!

⚡ 𝐒𝐢𝐬𝐭𝐞𝐦𝐚 𝐨𝐧𝐥𝐢𝐧𝐞 𝐞 𝐩𝐫𝐨𝐭𝐞𝐠𝐢𝐝𝐨.

━━━━━━━━━━━━━━

📊 𝐑𝐄𝐒𝐔𝐌𝐎 𝐃𝐎 𝐃𝐈𝐀

📤 𝐄𝐧𝐯𝐢𝐨𝐬: {envios}/30
📱 𝐌í𝐝𝐢𝐚𝐬: {midias}
🖼️ 𝐀́𝐥𝐛𝐮𝐧𝐬: {albuns}
⏰ 𝐀𝐠𝐞𝐧𝐝𝐚𝐝𝐨𝐬: {agendados}

━━━━━━━━━━━━━━

⚙️ 𝐀𝐜𝐞𝐬𝐬𝐨 𝐥𝐢𝐛𝐞𝐫𝐚𝐝𝐨 𝐚𝐨 𝐩𝐚𝐢𝐧𝐞𝐥.

🥷🏾 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐞 𝐭𝐨𝐭𝐚𝐥 𝐝𝐨 𝐬𝐢𝐬𝐭𝐞𝐦𝐚.


    await update.message.reply_text(
        mensagem
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

    adicionar_album(len(midias))

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

    adicionar_envio(1)

    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )