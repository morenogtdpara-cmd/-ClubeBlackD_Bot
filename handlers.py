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
ALBUM_LEGENDAS = {}
ALBUM_PAINEIS = {}

AGENDAMENTO_DADOS = {}


LEGENDA_FIXA_ALBUM = (
    "🔥 CONTEÚDO EXCLUSIVO LIBERADO 🔥\n\n"
    "🚀 Acesse nosso canal oficial:\n\n"
    "🤖 @ClubeBlackBot"
)


def montar_legenda_album(legenda_usuario):
    legenda_usuario = (legenda_usuario or "").strip()

    if legenda_usuario:
        return (
            f"{legenda_usuario}\n\n"
            f"{LEGENDA_FIXA_ALBUM}"
        )

    return LEGENDA_FIXA_ALBUM


def finalizar_album_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ FINALIZAR ÁLBUM",
                    callback_data="finalizar_album",
                )
            ]
        ]
    )


def texto_painel_album(quantidade):
    return (
        "🖼️ ÁLBUM EM MONTAGEM\n\n"
        f"Mídias adicionadas: {quantidade}/10\n\n"
        "Envie mais fotos ou vídeos ou toque em FINALIZAR ÁLBUM."
    )


def texto_painel_album_programado(quantidade):
    return (
        "🖼️ ÁLBUM PROGRAMADO\n\n"
        f"Mídias adicionadas: {quantidade}/10\n\n"
        "Envie mais fotos ou vídeos ou toque em FINALIZAR ÁLBUM."
    )


def texto_painel():
    return (
        "🥷🏾 BLACK PRIVATE\n\n"
        "⚜️ CENTRAL DE OPERAÇÕES\n\n"
        "Selecione um serviço:"
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bot privado.")
        return

    envios, midias, albuns, _ = pegar_relatorio()
    programadas = len(pegar_fila())

    mensagem = (
        "🥷🏾 BLACK PRIVATE\n\n"
        "👑 Bem-vindo de volta, Chefe.\n"
        "⚡ Sistema online e protegido.\n\n"
        "📊 RESUMO DO DIA\n\n"
        f"📤 Envios: {envios}/30\n"
        f"📱 Mídias: {midias}\n"
        f"🖼️ Álbuns: {albuns}\n"
        f"⏰ Programadas: {programadas}\n\n"
        "⚙️ Acesso liberado ao painel de controle."
    )

    await update.message.reply_text(mensagem)


async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        texto_painel(),
        reply_markup=painel_keyboard(),
    )


async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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
                "📋 PUBLICAÇÕES PROGRAMADAS\n\n"
                "Nenhuma publicação programada.",
                reply_markup=voltar_keyboard(),
            )
        else:
            await query.message.reply_text(
                "📋 PUBLICAÇÕES PROGRAMADAS\n\n"
                "Selecione uma publicação:",
                reply_markup=fila_keyboard(fila),
            )

        return

    if query.data.startswith("fila_pagina_"):
        pagina = int(
            query.data.replace("fila_pagina_", "")
        )

        fila = pegar_fila()

        await query.edit_message_text(
            "📋 PUBLICAÇÕES PROGRAMADAS\n\n"
            "Selecione uma publicação:",
            reply_markup=fila_keyboard(fila, pagina),
        )

        return

    if query.data.startswith("fila_item_"):
        indice = int(
            query.data.replace("fila_item_", "")
        )

        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await query.message.reply_text(
                "⚠️ Publicação não encontrada."
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
            quantidade = len(
                item.get("midias", [])
            )

            legenda = (
                item.get("conteudo", "").strip()
                or "Sem legenda personalizada"
            )

            detalhes = (
                f"Mídias: {quantidade}\n\n"
                f"Legenda:\n{legenda}"
            )
        else:
            conteudo = (
                item.get("conteudo", "").strip()
                or "Sem legenda"
            )

            detalhes = (
                f"Conteúdo:\n{conteudo}"
            )

        mensagem = (
            "📌 PUBLICAÇÃO PROGRAMADA\n\n"
            f"Data: {data_exibicao}\n"
            f"Horário: {horario}\n"
            f"Formato: {tipo}\n\n"
            f"{detalhes}"
        )

        await query.message.reply_text(
            mensagem,
            reply_markup=fila_item_keyboard(indice),
        )

        return

    if query.data.startswith("fila_remover_"):
        indice = int(
            query.data.replace("fila_remover_", "")
        )

        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await query.message.reply_text(
                "⚠️ Publicação não encontrada."
            )
            return

        remover_da_fila(indice)

        await query.edit_message_text(
            "🗑️ PUBLICAÇÃO CANCELADA\n\n"
            "A publicação foi removida das programadas.",
            reply_markup=voltar_keyboard(),
        )

        return

    if query.data == "divulgar":
        AGENDAMENTO_DADOS.pop(user_id, None)
        AGUARDANDO_DIVULGACAO.add(user_id)

        await query.message.reply_text(
            "📢 DIVULGAÇÃO IMEDIATA\n\n"
            "Envie a publicação. Ela será enviada imediatamente para o grupo."
        )

        return

    if query.data == "album":
        await query.message.reply_text(
            "🖼️ CENTRAL DE ÁLBUM\n\n"
            "Crie e envie um novo álbum.",
            reply_markup=album_keyboard(),
        )

        return

    if query.data == "album_agora":
        AGUARDANDO_DIVULGACAO.discard(user_id)

        ALBUM_MIDIAS[user_id] = []
        ALBUM_LEGENDAS[user_id] = ""

        mensagem_painel = await query.message.reply_text(
            texto_painel_album(0),
            reply_markup=finalizar_album_keyboard(),
        )

        ALBUM_PAINEIS[user_id] = {
            "chat_id": mensagem_painel.chat.id,
            "message_id": mensagem_painel.message_id,
        }

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
        "⏰ NOVO AGENDAMENTO\n\n"
        "Escolha o tipo de publicação:",
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
        "📄 PUBLICAÇÃO ÚNICA\n\n"
        "Envie um texto, uma foto ou um vídeo.",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_PUBLICACAO


async def escolher_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    AGENDAMENTO_DADOS[user_id] = {
        "modo": "album",
        "tipo": "album",
        "midias": [],
        "conteudo": "",
        "painel_chat_id": query.message.chat.id,
        "painel_message_id": query.message.message_id,
    }

    await query.edit_message_text(
        texto_painel_album_programado(0),
        reply_markup=finalizar_agendamento_album_keyboard(),
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
            "⚠️ TIPO NÃO SUPORTADO\n\n"
            "Envie um texto, uma foto ou um vídeo.",
            reply_markup=cancelar_agendamento_keyboard(),
        )

        return AGENDAMENTO_PUBLICACAO

    AGENDAMENTO_DADOS[user_id] = item

    await update.message.reply_text(
        "⏰ ESCOLHA O HORÁRIO\n\n"
        "Digite no formato 20:30.",
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
            "⚠️ Inicie o agendamento do álbum novamente."
        )

        return ConversationHandler.END

    midias = item.setdefault("midias", [])

    if len(midias) >= 10:
        await update.message.reply_text(
            "⚠️ LIMITE ATINGIDO\n\n"
            "O álbum pode ter no máximo 10 mídias."
        )

        return AGENDAMENTO_ALBUM

    legenda_recebida = (
        update.message.caption or ""
    ).strip()

    if update.message.photo:
        midias.append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id,
            }
        )

    elif update.message.video:
        midias.append(
            {
                "tipo": "video",
                "id": update.message.video.file_id,
            }
        )

    else:
        await update.message.reply_text(
            "⚠️ Envie somente fotos ou vídeos."
        )

        return AGENDAMENTO_ALBUM

    if not item.get("conteudo") and legenda_recebida:
        item["conteudo"] = legenda_recebida

    quantidade = len(midias)

    painel_chat_id = item.get("painel_chat_id")
    painel_message_id = item.get("painel_message_id")

    if painel_chat_id and painel_message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=painel_chat_id,
                message_id=painel_message_id,
                text=texto_painel_album_programado(
                    quantidade
                ),
                reply_markup=finalizar_agendamento_album_keyboard(),
            )
        except Exception as erro:
            print(
                "⚠️ Erro ao atualizar painel do álbum programado:",
                erro,
            )

    AGENDAMENTO_DADOS[user_id] = item

    return AGENDAMENTO_ALBUM


async def finalizar_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    item = AGENDAMENTO_DADOS.get(
        query.from_user.id,
        {},
    )

    midias = item.get("midias", [])

    if len(midias) < 2:
        await query.answer(
            "O álbum precisa ter pelo menos 2 mídias.",
            show_alert=True,
        )

        return AGENDAMENTO_ALBUM

    await query.edit_message_text(
        "⏰ ESCOLHA O HORÁRIO\n\n"
        "Digite no formato 20:30.",
        reply_markup=cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_HORARIO


async def receber_horario_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    horario_texto = (
        update.message.text or ""
    ).strip()

    try:
        horario_recebido = datetime.strptime(
            horario_texto,
            "%H:%M",
        )
    except ValueError:
        await update.message.reply_text(
            "⚠️ HORÁRIO INVÁLIDO\n\n"
            "Digite no formato 20:30.",
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
            "⚠️ HORÁRIO JÁ PASSOU\n\n"
            "Digite um horário mais à frente.",
            reply_markup=cancelar_agendamento_keyboard(),
        )

        return AGENDAMENTO_HORARIO

    item = AGENDAMENTO_DADOS.get(user_id)

    if not item:
        await update.message.reply_text(
            "⚠️ Publicação não encontrada."
        )

        return ConversationHandler.END

    item.pop("modo", None)
    item.pop("painel_chat_id", None)
    item.pop("painel_message_id", None)

    item["id"] = agora.strftime(
        "%Y%m%d%H%M%S%f"
    )

    item["data"] = agora.strftime(
        "%Y-%m-%d"
    )

    item["horario"] = horario_programado.strftime(
        "%H:%M"
    )

    item["enviado"] = False
    item["criado_em"] = agora.isoformat()

    adicionar_na_fila(item)
    AGENDAMENTO_DADOS.pop(user_id, None)

    if item.get("tipo") == "album":
        formato = (
            f"ÁLBUM • "
            f"{len(item.get('midias', []))} MÍDIAS"
        )
    else:
        formato = item.get(
            "tipo",
            "PUBLICAÇÃO",
        ).upper()

    await update.message.reply_text(
        "✅ PUBLICAÇÃO PROGRAMADA\n\n"
        f"Data: {agora.strftime('%d/%m/%Y')}\n"
        f"Horário: {horario_programado.strftime('%H:%M')}\n"
        f"Formato: {formato}",
        reply_markup=voltar_keyboard(),
    )

    return ConversationHandler.END


async def cancelar_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    AGENDAMENTO_DADOS.pop(
        query.from_user.id,
        None,
    )

    await query.edit_message_text(
        "❌ PROGRAMAÇÃO CANCELADA\n\n"
        "Nenhuma publicação foi salva.",
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

    midias = ALBUM_MIDIAS[user_id]

    if len(midias) >= 10:
        await update.message.reply_text(
            "⚠️ LIMITE ATINGIDO\n\n"
            "O álbum pode ter no máximo 10 mídias."
        )

        return ALBUM

    legenda_recebida = (
        update.message.caption or ""
    ).strip()

    if update.message.photo:
        midias.append(
            {
                "tipo": "foto",
                "id": update.message.photo[-1].file_id,
            }
        )

    elif update.message.video:
        midias.append(
            {
                "tipo": "video",
                "id": update.message.video.file_id,
            }
        )

    else:
        await update.message.reply_text(
            "⚠️ Envie somente fotos ou vídeos."
        )

        return ALBUM

    if (
        not ALBUM_LEGENDAS.get(user_id)
        and legenda_recebida
    ):
        ALBUM_LEGENDAS[user_id] = legenda_recebida

    quantidade = len(midias)
    painel = ALBUM_PAINEIS.get(user_id)

    if painel:
        try:
            await context.bot.edit_message_text(
                chat_id=painel["chat_id"],
                message_id=painel["message_id"],
                text=texto_painel_album(
                    quantidade
                ),
                reply_markup=finalizar_album_keyboard(),
            )
        except Exception as erro:
            print(
                "⚠️ Erro ao atualizar painel do álbum:",
                erro,
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
        await query.answer(
            "O álbum precisa ter pelo menos 2 mídias.",
            show_alert=True,
        )

        return ALBUM

    legenda_usuario = ALBUM_LEGENDAS.get(
        user_id,
        "",
    )

    legenda_completa = montar_legenda_album(
        legenda_usuario
    )

    lista_envio = []

    for indice, item in enumerate(midias[:10]):
        legenda = (
            legenda_completa
            if indice == 0
            else None
        )

        if item["tipo"] == "foto":
            lista_envio.append(
                InputMediaPhoto(
                    media=item["id"],
                    caption=legenda,
                )
            )

        elif item["tipo"] == "video":
            lista_envio.append(
                InputMediaVideo(
                    media=item["id"],
                    caption=legenda,
                )
            )

    try:
        await context.bot.send_media_group(
            chat_id=GROUP_ID,
            media=lista_envio,
        )
    except Exception as erro:
        await query.message.reply_text(
            "❌ ERRO AO ENVIAR ÁLBUM\n\n"
            f"{erro}"
        )

        return ALBUM

    adicionar_album(
        len(lista_envio)
    )

    await query.edit_message_text(
        "✅ ÁLBUM ENVIADO\n\n"
        "O álbum foi publicado com sucesso."
    )

    ALBUM_MIDIAS.pop(user_id, None)
    ALBUM_LEGENDAS.pop(user_id, None)
    ALBUM_PAINEIS.pop(user_id, None)

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
            "⚠️ TIPO NÃO SUPORTADO\n\n"
            "Envie um texto, uma foto ou um vídeo."
        )

        return

    AGUARDANDO_DIVULGACAO.discard(user_id)
    adicionar_envio(1)

    await update.message.reply_text(
        "✅ DIVULGAÇÃO ENVIADA\n\n"
        "A publicação foi enviada para o grupo."
    )