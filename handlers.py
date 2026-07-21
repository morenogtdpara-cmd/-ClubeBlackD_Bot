from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
)

from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK

from keyboards import (
    painel_keyboard,
    vip_keyboard,
    album_keyboard,
    fila_keyboard,
    fila_item_keyboard,
    agendamento_tipo_keyboard,
    finalizar_agendamento_album_keyboard,
    cancelar_agendamento_keyboard,
    voltar_keyboard,
)

from database import adicionar_envio, adicionar_album, pegar_relatorio

from fila import pegar_fila, remover_da_fila, adicionar_na_fila


ALBUM = 1
AGENDAMENTO_ESCOLHA = 3
AGENDAMENTO_PUBLICACAO = 4
AGENDAMENTO_ALBUM = 5
AGENDAMENTO_HORARIO = 6

AGUARDANDO_DIVULGACAO = set()
ALBUM_MIDIAS = {}
AGENDAMENTO_DADOS = {}


def texto_painel():
    return """
🥷🏾 𝐁𝐋𝐀𝐂𝐊 𝐏𝐑𝐈𝐕𝐀𝐓𝐄

⚜️ 𝐂𝐄𝐍𝐓𝐑𝐀𝐋 𝐃𝐄 𝐎𝐏𝐄𝐑𝐀ÇÕ𝐄𝐒

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌 𝐒𝐄𝐑𝐕𝐈Ç𝐎:

━━━━━━━━━━━━━━━━
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bot privado.")
        return

    envios, midias, albuns, _ = pegar_relatorio()
    programadas = len(pegar_fila())

    mensagem = f"""
🥷🏾 𝐁𝐋𝐀𝐂𝐊 𝐏𝐑𝐈𝐕𝐀𝐓𝐄

👑 𝐁𝐞𝐦-𝐯𝐢𝐧𝐝𝐨 𝐝𝐞 𝐯𝐨𝐥𝐭𝐚, 𝐂𝐡𝐞𝐟𝐞!

⚡ 𝐒𝐢𝐬𝐭𝐞𝐦𝐚 𝐨𝐧𝐥𝐢𝐧𝐞 𝐞 𝐩𝐫𝐨𝐭𝐞𝐠𝐢𝐝𝐨.

━━━━━━━━━━━━━━

📊 𝐑𝐄𝐒𝐔𝐌𝐎 𝐃𝐎 𝐃𝐈𝐀

📤 𝐄𝐧𝐯𝐢𝐨𝐬: {envios}/30
📱 𝐌í𝐝𝐢𝐚𝐬: {midias}
🖼️ 𝐀́𝐥𝐛𝐮𝐧𝐬: {albuns}
⏰ 𝐏𝐫𝐨𝐠𝐫𝐚𝐦𝐚𝐝𝐚𝐬: {programadas}

━━━━━━━━━━━━━━

⚙️ 𝐀𝐜𝐞𝐬𝐬𝐨 𝐥𝐢𝐛𝐞𝐫𝐚𝐝𝐨 𝐚𝐨 𝐩𝐚𝐢𝐧𝐞𝐥 𝐝𝐞 𝐜𝐨𝐧𝐭𝐫𝐨𝐥𝐞.

🥷🏾 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐞 𝐭𝐨𝐭𝐚𝐥 𝐝𝐨 𝐬𝐢𝐬𝐭𝐞𝐦𝐚.
"""

    await update.message.reply_text(mensagem)


async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        texto_painel(),
        reply_markup=painel_keyboard(),
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "voltar":
        await query.edit_message_text(
            texto_painel(),
            reply_markup=painel_keyboard(),
        )
        return

    if query.data == "fila":
        fila = pegar_fila()

        if not fila:
            await query.message.reply_text(
                """
📋 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÕ𝐄𝐒 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀𝐒

━━━━━━━━━━━━━━━━

⚠️ 𝐍𝐄𝐍𝐇𝐔𝐌𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀.
""",
                reply_markup=voltar_keyboard(),
            )
        else:
            await query.message.reply_text(
                """
📋 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÕ𝐄𝐒 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀𝐒

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎:
""",
                reply_markup=fila_keyboard(fila),
            )
        return

    if query.data.startswith("fila_pagina_"):
        pagina = int(query.data.replace("fila_pagina_", ""))
        fila = pegar_fila()

        await query.edit_message_text(
            """
📋 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÕ𝐄𝐒 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀𝐒

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐔𝐌𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎:
""",
            reply_markup=fila_keyboard(fila, pagina),
        )
        return

    if query.data.startswith("fila_item_"):
        indice = int(query.data.replace("fila_item_", ""))
        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await query.message.reply_text(
                "⚠️ 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐍Ã𝐎 𝐄𝐍𝐂𝐎𝐍𝐓𝐑𝐀𝐃𝐀."
            )
            return

        item = fila[indice]
        tipo = item.get("tipo", "publicação").upper()
        horario = item.get("horario", "SEM HORÁRIO")
        data_salva = item.get("data", "")

        try:
            data_exibicao = datetime.strptime(
                data_salva,
                "%Y-%m-%d",
            ).strftime("%d/%m/%Y")
        except ValueError:
            data_exibicao = data_salva or "SEM DATA"

        if item.get("tipo") == "album":
            quantidade = len(item.get("midias", []))
            detalhes = f"🖼️ 𝐌Í𝐃𝐈𝐀𝐒: {quantidade}"
        else:
            conteudo = item.get("conteudo", "").strip() or "SEM LEGENDA"
            detalhes = f"📝 𝐂𝐎𝐍𝐓𝐄Ú𝐃𝐎:\n\n{conteudo}"

        mensagem = f"""
📌 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀

━━━━━━━━━━━━━━━━

📅 𝐃𝐀𝐓𝐀: {data_exibicao}

⏰ 𝐇𝐎𝐑Á𝐑𝐈𝐎: {horario}

📦 𝐅𝐎𝐑𝐌𝐀𝐓𝐎: {tipo}

{detalhes}
"""

        await query.message.reply_text(
            mensagem,
            reply_markup=fila_item_keyboard(indice),
        )
        return

    if query.data.startswith("fila_remover_"):
        indice = int(query.data.replace("fila_remover_", ""))
        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await query.message.reply_text(
                "⚠️ 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐍Ã𝐎 𝐄𝐍𝐂𝐎𝐍𝐓𝐑𝐀𝐃𝐀."
            )
            return

        remover_da_fila(indice)

        await query.edit_message_text(
            """
🗑️ 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐂𝐀𝐍𝐂𝐄𝐋𝐀𝐃𝐀

━━━━━━━━━━━━━━━━

✅ 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐅𝐎𝐈 𝐑𝐄𝐌𝐎𝐕𝐈𝐃𝐀 𝐃𝐀𝐒 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀𝐒.
""",
            reply_markup=voltar_keyboard(),
        )
        return

    if query.data == "divulgar":
        AGENDAMENTO_DADOS.pop(user_id, None)
        AGUARDANDO_DIVULGACAO.add(user_id)

        await query.message.reply_text(
            """
📢 𝐌𝐎𝐃𝐎 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐀𝐓𝐈𝐕𝐀𝐃𝐎

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎.

⚡ 𝐄𝐋𝐀 𝐒𝐄𝐑Á 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐈𝐌𝐄𝐃𝐈𝐀𝐓𝐀𝐌𝐄𝐍𝐓𝐄.
"""
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
            reply_markup=album_keyboard(),
        )
        return

    if query.data == "album_agora":
        AGUARDANDO_DIVULGACAO.discard(user_id)
        ALBUM_MIDIAS[user_id] = []

        await query.message.reply_text(
            """
🖼️ 𝐌𝐎𝐃𝐎 𝐀́𝐋𝐁𝐔𝐌 𝐀𝐓𝐈𝐕𝐀𝐃𝐎

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐀𝐒 𝐅𝐎𝐓𝐎𝐒 𝐎𝐔 𝐕Í𝐃𝐄𝐎𝐒.
"""
        )
        return ALBUM


async def abrir_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    AGUARDANDO_DIVULGACAO.discard(user_id)
    AGENDAMENTO_DADOS[user_id] = {}

    await query.message.reply_text(
        """
⏰ 𝐍𝐎𝐕𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀

━━━━━━━━━━━━━━━━

𝐒𝐄𝐋𝐄𝐂𝐈𝐎𝐍𝐄 𝐎 𝐅𝐎𝐑𝐌𝐀𝐓𝐎:
""",
        reply_markup=agendamento_tipo_keyboard(),
    )

    return AGENDAMENTO_ESCOLHA


async def escolher_agendamento_unica(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    AGENDAMENTO_DADOS[query.from_user.id] = {
        "modo": "unica",
    }

    await query.edit_message_text(
        """
📄 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 Ú𝐍𝐈𝐂𝐀

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎.

𝐏𝐎𝐃𝐄 𝐒𝐄𝐑:

📝 𝐓𝐄𝐗𝐓𝐎
📸 𝐔𝐌𝐀 𝐅𝐎𝐓𝐎
🎥 𝐔𝐌 𝐕Í𝐃𝐄𝐎
""",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_PUBLICACAO


async def escolher_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    AGENDAMENTO_DADOS[query.from_user.id] = {
        "modo": "album",
        "tipo": "album",
        "midias": [],
        "conteudo": "",
    }

    await query.edit_message_text(
        """
🖼️ 𝐀́𝐋𝐁𝐔𝐌 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐎

━━━━━━━━━━━━━━━━

📤 𝐄𝐍𝐕𝐈𝐄 𝐃𝐄 𝟐 𝐀 𝟏𝟎 𝐅𝐎𝐓𝐎𝐒 𝐎𝐔 𝐕Í𝐃𝐄𝐎𝐒.

✅ 𝐐𝐔𝐀𝐍𝐃𝐎 𝐓𝐄𝐑𝐌𝐈𝐍𝐀𝐑, 𝐂𝐋𝐈𝐐𝐔𝐄 𝐄𝐌 𝐅𝐈𝐍𝐀𝐋𝐈𝐙𝐀𝐑.
""",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_ALBUM


async def receber_agendamento_publicacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    item = AGENDAMENTO_DADOS.get(user_id, {})
    item["modo"] = "unica"
    item["arquivo"] = None
    item["conteudo"] = ""

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
            """
⚠️ 𝐓𝐈𝐏𝐎 𝐃𝐄 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐍Ã𝐎 𝐒𝐔𝐏𝐎𝐑𝐓𝐀𝐃𝐎.

𝐄𝐍𝐕𝐈𝐄 𝐔𝐌 𝐓𝐄𝐗𝐓𝐎, 𝐔𝐌𝐀 𝐅𝐎𝐓𝐎 𝐎𝐔 𝐔𝐌 𝐕Í𝐃𝐄𝐎.
""",
            reply_markup=cancelar_agendamento_keyboard(),
        )
        return AGENDAMENTO_PUBLICACAO

    AGENDAMENTO_DADOS[user_id] = item

    await update.message.reply_text(
        """
⏰ 𝐄𝐒𝐂𝐎𝐋𝐇𝐀 𝐎 𝐇𝐎𝐑Á𝐑𝐈𝐎

━━━━━━━━━━━━━━━━

𝐃𝐈𝐆𝐈𝐓𝐄 𝐎 𝐇𝐎𝐑Á𝐑𝐈𝐎 𝐍𝐎 𝐅𝐎𝐑𝐌𝐀𝐓𝐎:

20:30
""",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_HORARIO


async def receber_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    item = AGENDAMENTO_DADOS.get(user_id)

    if not item or item.get("modo") != "album":
        await update.message.reply_text(
            "⚠️ 𝐈𝐍𝐈𝐂𝐈𝐄 𝐎 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎 𝐃𝐎 𝐀́𝐋𝐁𝐔𝐌 𝐍𝐎𝐕𝐀𝐌𝐄𝐍𝐓𝐄."
        )
        return ConversationHandler.END

    midias = item.setdefault("midias", [])

    if len(midias) >= 10:
        await update.message.reply_text(
            "⚠️ 𝐎 𝐋𝐈𝐌𝐈𝐓𝐄 𝐃𝐎 𝐀́𝐋𝐁𝐔𝐌 É 𝐃𝐄 𝟏𝟎 𝐌Í𝐃𝐈𝐀𝐒.",
            reply_markup=finalizar_agendamento_album_keyboard(),
        )
        return AGENDAMENTO_ALBUM

    if update.message.photo:
        midias.append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id,
                "caption": update.message.caption or "",
            }
        )

    elif update.message.video:
        midias.append(
            {
                "tipo": "video",
                "id": update.message.video.file_id,
                "caption": update.message.caption or "",
            }
        )

    else:
        await update.message.reply_text(
            "⚠️ 𝐄𝐍𝐕𝐈𝐄 𝐒𝐎𝐌𝐄𝐍𝐓𝐄 𝐅𝐎𝐓𝐎𝐒 𝐎𝐔 𝐕Í𝐃𝐄𝐎𝐒.",
            reply_markup=finalizar_agendamento_album_keyboard(),
        )
        return AGENDAMENTO_ALBUM

    if not item.get("conteudo") and update.message.caption:
        item["conteudo"] = update.message.caption

    quantidade = len(midias)

    await update.message.reply_text(
        f"✅ 𝐌Í𝐃𝐈𝐀 𝐀𝐃𝐈𝐂𝐈𝐎𝐍𝐀𝐃𝐀 ({quantidade}/10)",
        reply_markup=finalizar_agendamento_album_keyboard(),
    )

    return AGENDAMENTO_ALBUM


async def finalizar_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    item = AGENDAMENTO_DADOS.get(query.from_user.id, {})
    midias = item.get("midias", [])

    if len(midias) < 2:
        await query.message.reply_text(
            "⚠️ 𝐎 𝐀́𝐋𝐁𝐔𝐌 𝐏𝐑𝐄𝐂𝐈𝐒𝐀 𝐓𝐄𝐑 𝐏𝐄𝐋𝐎 𝐌𝐄𝐍𝐎𝐒 𝟐 𝐌Í𝐃𝐈𝐀𝐒.",
            reply_markup=finalizar_agendamento_album_keyboard(),
        )
        return AGENDAMENTO_ALBUM

    await query.message.reply_text(
        """
⏰ 𝐄𝐒𝐂𝐎𝐋𝐇𝐀 𝐎 𝐇𝐎𝐑Á𝐑𝐈𝐎

━━━━━━━━━━━━━━━━

𝐃𝐈𝐆𝐈𝐓𝐄 𝐎 𝐇𝐎𝐑Á𝐑𝐈𝐎 𝐍𝐎 𝐅𝐎𝐑𝐌𝐀𝐓𝐎:

20:30
""",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_HORARIO


async def receber_horario_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    horario_texto = (update.message.text or "").strip()

    try:
        horario_recebido = datetime.strptime(horario_texto, "%H:%M")
    except ValueError:
        await update.message.reply_text(
            """
⚠️ 𝐇𝐎𝐑Á𝐑𝐈𝐎 𝐈𝐍𝐕Á𝐋𝐈𝐃𝐎.

𝐃𝐈𝐆𝐈𝐓𝐄 𝐍𝐄𝐒𝐓𝐄 𝐅𝐎𝐑𝐌𝐀𝐓𝐎:

20:30
""",
            reply_markup=cancelar_agendamento_keyboard(),
        )
        return AGENDAMENTO_HORARIO

    fuso = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso)

    horario_programado = agora.replace(
        hour=horario_recebido.hour,
        minute=horario_recebido.minute,
        second=0,
        microsecond=0,
    )

    if horario_programado <= agora:
        await update.message.reply_text(
            """
⚠️ 𝐄𝐒𝐒𝐄 𝐇𝐎𝐑Á𝐑𝐈𝐎 𝐉Á 𝐏𝐀𝐒𝐒𝐎𝐔.

𝐃𝐈𝐆𝐈𝐓𝐄 𝐔𝐌 𝐇𝐎𝐑Á𝐑𝐈𝐎 𝐌𝐀𝐈𝐒 𝐀̀ 𝐅𝐑𝐄𝐍𝐓𝐄.
""",
            reply_markup=cancelar_agendamento_keyboard(),
        )
        return AGENDAMENTO_HORARIO

    item = AGENDAMENTO_DADOS.get(user_id)

    if not item:
        await update.message.reply_text(
            "⚠️ 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐍Ã𝐎 𝐄𝐍𝐂𝐎𝐍𝐓𝐑𝐀𝐃𝐀."
        )
        return ConversationHandler.END

    item.pop("modo", None)
    item["id"] = agora.strftime("%Y%m%d%H%M%S%f")
    item["data"] = agora.strftime("%Y-%m-%d")
    item["horario"] = horario_programado.strftime("%H:%M")
    item["enviado"] = False
    item["criado_em"] = agora.isoformat()

    adicionar_na_fila(item)
    AGENDAMENTO_DADOS.pop(user_id, None)

    if item.get("tipo") == "album":
        formato = f"ÁLBUM • {len(item.get('midias', []))} MÍDIAS"
    else:
        formato = item.get("tipo", "PUBLICAÇÃO").upper()

    await update.message.reply_text(
        f"""
✅ 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐀

━━━━━━━━━━━━━━━━

📅 𝐃𝐀𝐓𝐀: {agora.strftime('%d/%m/%Y')}

⏰ 𝐇𝐎𝐑Á𝐑𝐈𝐎: {horario_programado.strftime('%H:%M')}

📦 𝐅𝐎𝐑𝐌𝐀𝐓𝐎: {formato}
""",
        reply_markup=voltar_keyboard(),
    )

    return ConversationHandler.END


async def cancelar_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    AGENDAMENTO_DADOS.pop(query.from_user.id, None)

    await query.edit_message_text(
        """
❌ 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀ÇÃ𝐎 𝐂𝐀𝐍𝐂𝐄𝐋𝐀𝐃𝐀

━━━━━━━━━━━━━━━━

𝐍𝐄𝐍𝐇𝐔𝐌𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐅𝐎𝐈 𝐒𝐀𝐋𝐕𝐀.
""",
        reply_markup=painel_keyboard(),
    )

    return ConversationHandler.END


async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if user_id not in ALBUM_MIDIAS:
        ALBUM_MIDIAS[user_id] = []

    if update.message.photo:
        ALBUM_MIDIAS[user_id].append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id,
            }
        )

    elif update.message.video:
        ALBUM_MIDIAS[user_id].append(
            {
                "tipo": "video",
                "id": update.message.video.file_id,
            }
        )

    finalizar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ 𝐅𝐈𝐍𝐀𝐋𝐈𝐙𝐀𝐑 𝐀́𝐋𝐁𝐔𝐌",
                    callback_data="finalizar_album",
                )
            ]
        ]
    )

    quantidade = len(ALBUM_MIDIAS[user_id])

    await update.message.reply_text(
        f"✅ 𝐌Í𝐃𝐈𝐀 𝐀𝐃𝐈𝐂𝐈𝐎𝐍𝐀𝐃𝐀 ({quantidade})",
        reply_markup=finalizar,
    )

    return ALBUM


async def finalizar_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    midias = ALBUM_MIDIAS.get(user_id, [])

    if len(midias) < 2:
        await query.message.reply_text(
            "⚠️ 𝐎 𝐀́𝐋𝐁𝐔𝐌 𝐏𝐑𝐄𝐂𝐈𝐒𝐀 𝐓𝐄𝐑 𝐏𝐄𝐋𝐎 𝐌𝐄𝐍𝐎𝐒 𝟐 𝐌Í𝐃𝐈𝐀𝐒."
        )
        return ALBUM

    lista_envio = []

    for item in midias[:10]:
        if item["tipo"] == "foto":
            lista_envio.append(InputMediaPhoto(media=item["id"]))
        elif item["tipo"] == "video":
            lista_envio.append(InputMediaVideo(media=item["id"]))

    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=lista_envio,
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🔥 𝐄𝐍𝐓𝐑𝐄 𝐍𝐎 𝐕𝐈𝐏:",
        reply_markup=vip_keyboard(VIP_LINK),
    )

    adicionar_album(len(lista_envio))

    await query.message.reply_text(
        "✅ 𝐀́𝐋𝐁𝐔𝐌 𝐄𝐍𝐕𝐈𝐀𝐃𝐎 𝐂𝐎𝐌 𝐒𝐔𝐂𝐄𝐒𝐒𝐎."
    )

    ALBUM_MIDIAS.pop(user_id, None)
    return ConversationHandler.END


async def receber_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if user_id not in AGUARDANDO_DIVULGACAO:
        return

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=update.message.caption or "",
            reply_markup=vip_keyboard(VIP_LINK),
        )

    elif update.message.video:
        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=update.message.caption or "",
            reply_markup=vip_keyboard(VIP_LINK),
        )

    elif update.message.text:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=update.message.text,
            reply_markup=vip_keyboard(VIP_LINK),
        )

    else:
        await update.message.reply_text(
            """
⚠️ 𝐓𝐈𝐏𝐎 𝐃𝐄 𝐌𝐄𝐍𝐒𝐀𝐆𝐄𝐌 𝐍Ã𝐎 𝐒𝐔𝐏𝐎𝐑𝐓𝐀𝐃𝐎.

𝐄𝐍𝐕𝐈𝐄 𝐔𝐌 𝐓𝐄𝐗𝐓𝐎, 𝐔𝐌𝐀 𝐅𝐎𝐓𝐎 𝐎𝐔 𝐔𝐌 𝐕Í𝐃𝐄𝐎.
"""
        )
        return

    AGUARDANDO_DIVULGACAO.discard(user_id)
    adicionar_envio(1)

    await update.message.reply_text(
        """
✅ 𝐃𝐈𝐕𝐔𝐋𝐆𝐀ÇÃ𝐎 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐂𝐎𝐌 𝐒𝐔𝐂𝐄𝐒𝐒𝐎.

⚡ 𝐀 𝐏𝐔𝐁𝐋𝐈𝐂𝐀ÇÃ𝐎 𝐅𝐎𝐈 𝐄𝐍𝐕𝐈𝐀𝐃𝐀 𝐃𝐈𝐑𝐄𝐓𝐀𝐌𝐄𝐍𝐓𝐄 𝐏𝐀𝐑𝐀 𝐎 𝐆𝐑𝐔𝐏𝐎.
"""
    )
