from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
)

from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK

from keyboards import (
    painel_keyboard,
    vip_keyboard,
    album_keyboard,
    fila_keyboard,
    fila_item_keyboard
)

from database import (
    adicionar_envio,
    adicionar_album,
    pegar_relatorio
)

from fila import (
    pegar_fila,
    remover_da_fila,
    adicionar_na_fila
)


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

    mensagem = f"""
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

⚙️ 𝐀𝐜𝐞𝐬𝐬𝐨 𝐥𝐢𝐛𝐞𝐫𝐚𝐝𝐨 𝐚𝐨 𝐩𝐚𝐢𝐧𝐞𝐥 𝐝𝐞 𝐜𝐨𝐧𝐭𝐫𝐨𝐥𝐞.

🥷🏾 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐞 𝐭𝐨𝐭𝐚𝐥 𝐝𝐨 𝐬𝐢𝐬𝐭𝐞𝐦𝐚.
"""

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
        """
🥷🏾 𝐁𝐋𝐀𝐂𝐊 𝐏𝐑𝐈𝐕𝐀𝐓𝐄

⚜️ 𝐂𝐄𝐍𝐓𝐑𝐀𝐋 𝐃𝐄 𝐎𝐏𝐄𝐑𝐀ÇÕ𝐄𝐒

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌 𝐒𝐄𝐑𝐕𝐈Ç𝐎:

━━━━━━━━━━━━━━━━
""",
        reply_markup=painel_keyboard()
    )


async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "fila":

        fila = pegar_fila()

        if not fila:

            await query.message.reply_text(
                "⏰ FILA DE DIVULGAÇÃO\n\n"
                "Nenhuma divulgação na fila."
            )

        else:

            await query.message.reply_text(
                "⏰ FILA DE DIVULGAÇÃO\n\n"
                "Escolha uma divulgação:",
                reply_markup=fila_keyboard(fila)
            )

        return

    if query.data.startswith("fila_item_"):

        indice = int(
            query.data.replace(
                "fila_item_",
                ""
            )
        )

        fila = pegar_fila()

        if 0 <= indice < len(fila):

            item = fila[indice]

            mensagem = (
                "📌 DIVULGAÇÃO SELECIONADA\n\n"
                f"📝 Conteúdo:\n"
                f"{item.get('conteudo', 'Sem conteúdo')}\n\n"
                f"⏰ Horário:\n"
                f"{item.get('horario', 'Sem horário')}\n\n"
                f"📊 Status:\n"
                f"{'✅ Enviado' if item.get('enviado') else '⏳ Aguardando envio'}"
            )

            await query.message.reply_text(
                mensagem,
                reply_markup=fila_item_keyboard()
            )

        return

    if query.data == "fila_enviar":

        fila = pegar_fila()

        if not fila:

            await query.message.reply_text(
                "⚠️ Fila vazia."
            )

            return

        item = fila[0]

        tipo = item.get("tipo")
        arquivo = item.get("arquivo")
        conteudo = item.get("conteudo", "")

        if tipo == "foto":

            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=arquivo,
                caption=conteudo,
                reply_markup=vip_keyboard(VIP_LINK)
            )

        elif tipo == "video":

            await context.bot.send_video(
                chat_id=GROUP_ID,
                video=arquivo,
                caption=conteudo,
                reply_markup=vip_keyboard(VIP_LINK)
            )

        elif tipo == "texto":

            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=conteudo,
                reply_markup=vip_keyboard(VIP_LINK)
            )

        remover_da_fila(0)

        adicionar_envio(1)

        await query.message.reply_text(
            "🚀 Divulgação enviada e removida da fila."
        )

        return

    if query.data == "fila_remover":

        remover_da_fila(0)

        await query.message.reply_text(
            "🗑 Divulgação removida da fila."
        )

        return

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
            """
🖼️ 𝐂𝐄𝐍𝐓𝐑𝐀𝐋 𝐃𝐄 𝐀́𝐋𝐁𝐔𝐌

━━━━━━━━━━━━━━━━

📸 𝐂𝐑𝐈𝐄 𝐄 𝐄𝐍𝐕𝐈𝐄 𝐔𝐌 𝐍𝐎𝐕𝐎 𝐀́𝐋𝐁𝐔𝐌.

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌𝐀 𝐎𝐏ÇÃ𝐎:
""",
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

    adicionar_album(
        len(midias)
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

    item = {
        "conteudo": "",
        "tipo": "",
        "arquivo": None,
        "horario": "Agora",
        "enviado": False
    }

    if update.message.photo:

        item["tipo"] = "foto"
        item["arquivo"] = update.message.photo[-1].file_id
        item["conteudo"] = update.message.caption or ""

    elif update.message.video:

        item["tipo"] = "video"
        item["arquivo"] = update.message.video.file_id
        item["conteudo"] = update.message.caption or ""

    elif update.message.text:

        item["tipo"] = "texto"
        item["conteudo"] = update.message.text

    else:

        await update.message.reply_text(
            "⚠️ Tipo de mensagem não suportado."
        )

        return

    adicionar_na_fila(item)

    AGUARDANDO_DIVULGACAO.remove(
        user_id
    )

    await update.message.reply_text(
        "⏳ Divulgação adicionada na fila."
    )