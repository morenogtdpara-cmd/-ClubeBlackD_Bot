from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler
)

from config import (
    ADMIN_ID,
    GROUP_ID,
    VIP_LINK
)

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
    remover_da_fila
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

    # VOLTAR AO PAINEL PRINCIPAL
    if query.data == "voltar":

        await query.edit_message_text(
            """
🥷🏾 𝐁𝐋𝐀𝐂𝐊 𝐏𝐑𝐈𝐕𝐀𝐓𝐄

⚜️ 𝐂𝐄𝐍𝐓𝐑𝐀𝐋 𝐃𝐄 𝐎𝐏𝐄𝐑𝐀ÇÕ𝐄𝐒

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌 𝐒𝐄𝐑𝐕𝐈Ç𝐎:

━━━━━━━━━━━━━━━━
""",
            reply_markup=painel_keyboard()
        )

        return

    # FILA
    if query.data == "fila":

        fila = pegar_fila()

        if not fila:

            await query.message.reply_text(
                """
📋 𝐅𝐈𝐋𝐀 𝐃𝐄 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎

━━━━━━━━━━━━━━━━

⚠️ 𝐍𝐄𝐍𝐇𝐔𝐌𝐀 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐍𝐀 𝐅𝐈𝐋𝐀.
"""
            )

        else:

            await query.message.reply_text(
                """
📋 𝐅𝐈𝐋𝐀 𝐃𝐄 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎

━━━━━━━━━━━━━━━━

𝐄𝐒𝐂𝐎𝐋𝐇𝐀 𝐔𝐌𝐀 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎:
""",
                reply_markup=fila_keyboard(fila)
            )

        return

    # ITEM DA FILA
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
                "📌 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐀𝐃𝐀\n\n"
                "━━━━━━━━━━━━━━━━\n\n"
                f"📝 𝐂𝐎𝐍𝐓𝐄Ú𝐃𝐎:\n"
                f"{item.get('conteudo', 'Sem conteúdo')}\n\n"
                f"⏰ 𝐇𝐎𝐑Á𝐑𝐈𝐎:\n"
                f"{item.get('horario', 'Sem horário')}\n\n"
                f"📊 𝐒𝐓𝐀𝐓𝐔𝐒:\n"
                f"{'✅ ENVIADO' if item.get('enviado') else '⏳ AGUARDANDO ENVIO'}"
            )

            await query.message.reply_text(
                mensagem,
                reply_markup=fila_item_keyboard()
            )

        return

    # ENVIAR ITEM DA FILA
    if query.data == "fila_enviar":

        fila = pegar_fila()

        if not fila:

            await query.message.reply_text(
                "⚠️ 𝐅𝐈𝐋𝐀 𝐕𝐀𝐙𝐈𝐀."
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
            "🚀 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐄 𝐑𝐄𝐌𝐎𝐕𝐈𝐃𝐀 𝐃𝐀 𝐅𝐈𝐋𝐀."
        )

        return

    # REMOVER ITEM DA FILA
    if query.data == "fila_remover":

        fila = pegar_fila()

        if not fila:

            await query.message.reply_text(
                "⚠️ 𝐅𝐈𝐋𝐀 𝐕𝐀𝐙𝐈𝐀."
            )

            return

        remover_da_fila(0)

        await query.message.reply_text(
            "🗑️ 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐑𝐄𝐌𝐎𝐕𝐈𝐃𝐀 𝐃𝐀 𝐅𝐈𝐋𝐀."
        )

        return

    # ATIVAR MODO DIVULGAÇÃO
    if query.data == "divulgar":

        AGUARDANDO_DIVULGACAO.add(
            query.from_user.id
        )

        await query.message.reply_text(
            """
📢 𝐌𝐎𝐃𝐎 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐀𝐓𝐈𝐕𝐀𝐃𝐎

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎.

⚡ 𝐄𝐋𝐀 𝐒𝐄𝐑Á 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐈𝐌𝐄𝐃𝐈𝐀𝐓𝐀𝐌𝐄𝐍𝐓𝐄.
"""
        )

        return

    # CENTRAL DE ÁLBUM
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

    # INICIAR NOVO ÁLBUM
    if query.data == "album_agora":

        ALBUM_MIDIAS[query.from_user.id] = []

        await query.message.reply_text(
            """
🖼️ 𝐌𝐎𝐃𝐎 𝐀́𝐋𝐁𝐔𝐌 𝐀𝐓𝐈𝐕𝐀𝐃𝐎

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐀𝐒 𝐅𝐎𝐓𝐎𝐒 𝐎𝐔 𝐕Í𝐃𝐄𝐎𝐒.
"""
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
                "✅ 𝐅𝐈𝐍𝐀𝐋𝐈𝐙𝐀𝐑 𝐀́𝐋𝐁𝐔𝐌",
                callback_data="finalizar_album"
            )
        ]
    ])

    quantidade = len(
        ALBUM_MIDIAS[user_id]
    )

    await update.message.reply_text(
        f"✅ 𝐌Í𝐃𝐈𝐀 𝐀𝐃𝐈𝐂𝐈𝐎𝐍𝐀𝐃𝐀 ({quantidade})",
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
            "⚠️ 𝐍𝐄𝐍𝐇𝐔𝐌𝐀 𝐌Í𝐃𝐈𝐀 𝐍𝐎 𝐀́𝐋𝐁𝐔𝐌."
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
        text="🔥 𝐄𝐍𝐓𝐑𝐄 𝐍𝐎 𝐕𝐈𝐏:",
        reply_markup=vip_keyboard(VIP_LINK)
    )

    adicionar_album(
        len(midias)
    )

    await query.message.reply_text(
        "✅ 𝐀́𝐋𝐁𝐔𝐌 𝐄𝐍𝐕𝐈𝐀𝐃𝐎 𝐂𝐎𝐌 𝐒𝐔𝐂𝐄𝐒𝐒𝐎."
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

    # FOTO
    if update.message.photo:

        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=update.message.caption or "",
            reply_markup=vip_keyboard(VIP_LINK)
        )

    # VÍDEO
    elif update.message.video:

        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=update.message.caption or "",
            reply_markup=vip_keyboard(VIP_LINK)
        )

    # TEXTO
    elif update.message.text:

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=update.message.text,
            reply_markup=vip_keyboard(VIP_LINK)
        )

    # TIPO NÃO SUPORTADO
    else:

        await update.message.reply_text(
            """
⚠️ 𝐓𝐈𝐏𝐎 𝐃𝐄 𝐌𝐄𝐍𝐒𝐀𝐆𝐄𝐌 𝐍Ã𝐎 𝐒𝐔𝐏𝐎𝐑𝐓𝐀𝐃𝐎.

𝐄𝐍𝐕𝐈𝐄 𝐔𝐌 𝐓𝐄𝐗𝐓𝐎, 𝐔𝐌𝐀 𝐅𝐎𝐓𝐎 𝐎𝐔 𝐔𝐌 𝐕Í𝐃𝐄𝐎.
"""
        )

        return

    AGUARDANDO_DIVULGACAO.discard(
        user_id
    )

    adicionar_envio(1)

    await update.message.reply_text(
        """
✅ 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐂𝐎𝐌 𝐒𝐔𝐂𝐄𝐒𝐒𝐎.

⚡ 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐅𝐎𝐈 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐃𝐈𝐑𝐄𝐓𝐀𝐌𝐄𝐍𝐓𝐄 𝐏𝐀𝐑𝐀 𝐎 𝐆𝐑𝐔𝐏𝐎.
"""
    )