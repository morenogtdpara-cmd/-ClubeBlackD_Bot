from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    InputMediaPhoto,
    InputMediaVideo,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from database import adicionar_album, adicionar_envio
from fila import adicionar_na_fila, pegar_fila, remover_da_fila
from keyboards import (
    agendamento_tipo_keyboard,
    album_keyboard,
    cancelar_agendamento_keyboard,
    cancelar_processo_keyboard,
    fila_item_keyboard,
    fila_keyboard,
    finalizar_agendamento_album_keyboard,
    finalizar_album_keyboard,
    processo_finalizado_keyboard,
    vip_keyboard,
    voltar_keyboard,
)
from painel import (
    apagar_mensagem_segura,
    editar_painel,
    limpar_mensagens_temporarias,
    mostrar_painel_principal,
    registrar_mensagem_entrada,
)


ALBUM = 1
AGENDAMENTO_ESCOLHA = 3
AGENDAMENTO_PUBLICACAO = 4
AGENDAMENTO_ALBUM = 5
AGENDAMENTO_HORARIO = 6

AGUARDANDO_DIVULGACAO = set()
ALBUM_MIDIAS = {}
ALBUM_LEGENDAS = {}
AGENDAMENTO_DADOS = {}


LEGENDA_FIXA_ALBUM = (
    "ð¥ CONTEÃDO EXCLUSIVO LIBERADO\n\n"
    "ð Acesse nosso canal oficial:\n\n"
    "ð¤ @ClubeBlackBot"
)


def montar_legenda_album(legenda_usuario):
    legenda_usuario = (legenda_usuario or "").strip()

    if legenda_usuario:
        return f"{legenda_usuario}\n\n{LEGENDA_FIXA_ALBUM}"

    return LEGENDA_FIXA_ALBUM


def texto_painel_album(quantidade):
    return (
        "ð¼ï¸ ÃLBUM EM MONTAGEM\n\n"
        f"MÃ­dias adicionadas: {quantidade}/10\n\n"
        "Envie mais fotos ou vÃ­deos ou toque em FINALIZAR ÃLBUM."
    )


def texto_painel_album_programado(quantidade):
    return (
        "ð¼ï¸ ÃLBUM PROGRAMADO\n\n"
        f"MÃ­dias adicionadas: {quantidade}/10\n\n"
        "Envie mais fotos ou vÃ­deos ou toque em FINALIZAR ÃLBUM."
    )


def encerrar_estados(user_id):
    AGUARDANDO_DIVULGACAO.discard(user_id)
    ALBUM_MIDIAS.pop(user_id, None)
    ALBUM_LEGENDAS.pop(user_id, None)
    AGENDAMENTO_DADOS.pop(user_id, None)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    encerrar_estados(update.effective_user.id)

    if update.effective_message:
        await apagar_mensagem_segura(
            context.bot,
            update.effective_chat.id,
            update.effective_message.message_id,
        )

    await limpar_mensagens_temporarias(
        context,
        update.effective_chat.id,
    )
    await mostrar_painel_principal(update, context)

    return ConversationHandler.END


async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    return await start(update, context)


async def finalizar_processo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Acesso nÃ£o autorizado.",
            show_alert=True,
        )
        return ConversationHandler.END

    await query.answer()
    encerrar_estados(query.from_user.id)

    await limpar_mensagens_temporarias(
        context,
        update.effective_chat.id,
    )
    await mostrar_painel_principal(update, context)

    return ConversationHandler.END


async def cancelar_processo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query:
        if query.from_user.id != ADMIN_ID:
            await query.answer(
                "Acesso nÃ£o autorizado.",
                show_alert=True,
            )
            return ConversationHandler.END

        await query.answer()
        user_id = query.from_user.id
    else:
        if update.effective_user.id != ADMIN_ID:
            return ConversationHandler.END

        user_id = update.effective_user.id

        if update.effective_message:
            await apagar_mensagem_segura(
                context.bot,
                update.effective_chat.id,
                update.effective_message.message_id,
            )

    encerrar_estados(user_id)

    await limpar_mensagens_temporarias(
        context,
        update.effective_chat.id,
    )
    await mostrar_painel_principal(update, context)

    return ConversationHandler.END


async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Acesso nÃ£o autorizado.",
            show_alert=True,
        )
        return

    if query.data == "finalizar_processo":
        return await finalizar_processo(update, context)

    if query.data in {
        "cancelar_processo",
        "cancelar_agendamento",
    }:
        return await cancelar_processo(update, context)

    await query.answer()

    if query.data == "voltar":
        encerrar_estados(query.from_user.id)
        await limpar_mensagens_temporarias(
            context,
            update.effective_chat.id,
        )
        await mostrar_painel_principal(update, context)
        return

    if query.data == "fila":
        fila = pegar_fila()

        if not fila:
            await editar_painel(
                update,
                context,
                "ð PUBLICAÃÃES PROGRAMADAS\n\n"
                "Nenhuma publicaÃ§Ã£o programada.",
                voltar_keyboard(),
            )
        else:
            await editar_painel(
                update,
                context,
                "ð PUBLICAÃÃES PROGRAMADAS\n\n"
                "Selecione uma publicaÃ§Ã£o:",
                fila_keyboard(fila),
            )

        return

    if query.data.startswith("fila_pagina_"):
        pagina = int(query.data.replace("fila_pagina_", ""))
        fila = pegar_fila()

        await editar_painel(
            update,
            context,
            "ð PUBLICAÃÃES PROGRAMADAS\n\n"
            "Selecione uma publicaÃ§Ã£o:",
            fila_keyboard(fila, pagina),
        )
        return

    if query.data.startswith("fila_item_"):
        indice = int(query.data.replace("fila_item_", ""))
        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await editar_painel(
                update,
                context,
                "â ï¸ PublicaÃ§Ã£o nÃ£o encontrada.",
                voltar_keyboard(),
            )
            return

        item = fila[indice]
        tipo = item.get("tipo", "publicaÃ§Ã£o").upper()
        horario = item.get("horario", "SEM HORÃRIO")
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
            legenda = (
                item.get("conteudo", "").strip()
                or "Sem legenda personalizada"
            )
            detalhes = (
                f"MÃ­dias: {quantidade}\n\n"
                f"Legenda:\n{legenda}"
            )
        else:
            conteudo = (
                item.get("conteudo", "").strip()
                or "Sem legenda"
            )
            detalhes = f"ConteÃºdo:\n{conteudo}"

        mensagem = (
            "ð PUBLICAÃÃO PROGRAMADA\n\n"
            f"Data: {data_exibicao}\n"
            f"HorÃ¡rio: {horario}\n"
            f"Formato: {tipo}\n\n"
            f"{detalhes}"
        )

        await editar_painel(
            update,
            context,
            mensagem,
            fila_item_keyboard(indice),
        )
        return

    if query.data.startswith("fila_remover_"):
        indice = int(query.data.replace("fila_remover_", ""))
        fila = pegar_fila()

        if not 0 <= indice < len(fila):
            await editar_painel(
                update,
                context,
                "â ï¸ PublicaÃ§Ã£o nÃ£o encontrada.",
                voltar_keyboard(),
            )
            return

        remover_da_fila(indice)

        await editar_painel(
            update,
            context,
            "ðï¸ PUBLICAÃÃO CANCELADA\n\n"
            "A publicaÃ§Ã£o foi removida das programadas.",
            processo_finalizado_keyboard(),
        )
        return

    if query.data == "divulgar":
        encerrar_estados(query.from_user.id)
        AGUARDANDO_DIVULGACAO.add(query.from_user.id)

        await editar_painel(
            update,
            context,
            "ð¢ DIVULGAÃÃO IMEDIATA\n\n"
            "Envie um texto, uma foto ou um vÃ­deo.\n\n"
            "A publicaÃ§Ã£o serÃ¡ enviada imediatamente para o grupo.",
            cancelar_processo_keyboard(),
        )
        return

    if query.data == "album":
        await editar_painel(
            update,
            context,
            "ð¼ï¸ CENTRAL DE ÃLBUM\n\n"
            "Crie e envie um novo Ã¡lbum.",
            album_keyboard(),
        )
        return

    await mostrar_painel_principal(update, context)


async def abrir_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Acesso nÃ£o autorizado.",
            show_alert=True,
        )
        return ConversationHandler.END

    await query.answer()
    user_id = query.from_user.id
    encerrar_estados(user_id)

    ALBUM_MIDIAS[user_id] = []
    ALBUM_LEGENDAS[user_id] = ""

    await editar_painel(
        update,
        context,
        texto_painel_album(0),
        finalizar_album_keyboard(),
    )

    return ALBUM


async def abrir_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Acesso nÃ£o autorizado.",
            show_alert=True,
        )
        return ConversationHandler.END

    await query.answer()
    user_id = query.from_user.id
    encerrar_estados(user_id)
    AGENDAMENTO_DADOS[user_id] = {}

    await editar_painel(
        update,
        context,
        "â° NOVO AGENDAMENTO\n\n"
        "Escolha o tipo de publicaÃ§Ã£o:",
        agendamento_tipo_keyboard(),
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

    await editar_painel(
        update,
        context,
        "ð PUBLICAÃÃO ÃNICA\n\n"
        "Envie um texto, uma foto ou um vÃ­deo.",
        cancelar_agendamento_keyboard(),
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

    await editar_painel(
        update,
        context,
        texto_painel_album_programado(0),
        finalizar_agendamento_album_keyboard(),
    )

    return AGENDAMENTO_ALBUM


async def receber_agendamento_publicacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await registrar_mensagem_entrada(update)
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
        await editar_painel(
            update,
            context,
            "â ï¸ TIPO NÃO SUPORTADO\n\n"
            "Envie um texto, uma foto ou um vÃ­deo.",
            cancelar_agendamento_keyboard(),
        )
        return AGENDAMENTO_PUBLICACAO

    AGENDAMENTO_DADOS[user_id] = item

    await editar_painel(
        update,
        context,
        "â° ESCOLHA O HORÃRIO\n\n"
        "Digite no formato 20:30.",
        cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_HORARIO


async def receber_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await registrar_mensagem_entrada(update)
    user_id = update.effective_user.id
    item = AGENDAMENTO_DADOS.get(user_id)

    if not item or item.get("modo") != "album":
        await editar_painel(
            update,
            context,
            "â ï¸ O agendamento do Ã¡lbum foi perdido.\n\n"
            "Finalize para voltar ao painel.",
            processo_finalizado_keyboard(),
        )
        return ConversationHandler.END

    midias = item.setdefault("midias", [])

    if len(midias) >= 10:
        await editar_painel(
            update,
            context,
            "â ï¸ LIMITE ATINGIDO\n\n"
            "O Ã¡lbum pode ter no mÃ¡ximo 10 mÃ­dias.",
            finalizar_agendamento_album_keyboard(),
        )
        return AGENDAMENTO_ALBUM

    legenda_recebida = (update.message.caption or "").strip()

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
        await editar_painel(
            update,
            context,
            "â ï¸ Envie somente fotos ou vÃ­deos.",
            finalizar_agendamento_album_keyboard(),
        )
        return AGENDAMENTO_ALBUM

    if not item.get("conteudo") and legenda_recebida:
        item["conteudo"] = legenda_recebida

    AGENDAMENTO_DADOS[user_id] = item

    await editar_painel(
        update,
        context,
        texto_painel_album_programado(len(midias)),
        finalizar_agendamento_album_keyboard(),
    )

    return AGENDAMENTO_ALBUM


async def finalizar_agendamento_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    item = AGENDAMENTO_DADOS.get(query.from_user.id, {})
    midias = item.get("midias", [])

    if len(midias) < 2:
        await query.answer(
            "O Ã¡lbum precisa ter pelo menos 2 mÃ­dias.",
            show_alert=True,
        )
        return AGENDAMENTO_ALBUM

    await query.answer()

    await editar_painel(
        update,
        context,
        "â° ESCOLHA O HORÃRIO\n\n"
        "Digite no formato 20:30.",
        cancelar_agendamento_keyboard(),
    )

    return AGENDAMENTO_HORARIO


async def receber_horario_agendamento(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await registrar_mensagem_entrada(update)
    user_id = update.effective_user.id
    horario_texto = (update.message.text or "").strip()

    try:
        horario_recebido = datetime.strptime(
            horario_texto,
            "%H:%M",
        )
    except ValueError:
        await editar_painel(
            update,
            context,
            "â ï¸ HORÃRIO INVÃLIDO\n\n"
            "Digite no formato 20:30.",
            cancelar_agendamento_keyboard(),
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
        await editar_painel(
            update,
            context,
            "â ï¸ HORÃRIO JÃ PASSOU\n\n"
            "Digite um horÃ¡rio mais Ã  frente.",
            cancelar_agendamento_keyboard(),
        )
        return AGENDAMENTO_HORARIO

    item = AGENDAMENTO_DADOS.get(user_id)

    if not item:
        await editar_painel(
            update,
            context,
            "â ï¸ PublicaÃ§Ã£o nÃ£o encontrada.",
            processo_finalizado_keyboard(),
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
        formato = (
            f"ÃLBUM â¢ {len(item.get('midias', []))} MÃDIAS"
        )
    else:
        formato = item.get("tipo", "PUBLICAÃÃO").upper()

    await editar_painel(
        update,
        context,
        "â PUBLICAÃÃO PROGRAMADA\n\n"
        f"Data: {agora.strftime('%d/%m/%Y')}\n"
        f"HorÃ¡rio: {horario_programado.strftime('%H:%M')}\n"
        f"Formato: {formato}\n\n"
        "Toque abaixo para apagar as mensagens usadas e voltar ao painel.",
        processo_finalizado_keyboard(),
    )

    return ConversationHandler.END


async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await registrar_mensagem_entrada(update)
    user_id = update.effective_user.id
    midias = ALBUM_MIDIAS.setdefault(user_id, [])

    if len(midias) >= 10:
        await editar_painel(
            update,
            context,
            "â ï¸ LIMITE ATINGIDO\n\n"
            "O Ã¡lbum pode ter no mÃ¡ximo 10 mÃ­dias.",
            finalizar_album_keyboard(),
        )
        return ALBUM

    legenda_recebida = (update.message.caption or "").strip()

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
        await editar_painel(
            update,
            context,
            "â ï¸ Envie somente fotos ou vÃ­deos.",
            finalizar_album_keyboard(),
        )
        return ALBUM

    if not ALBUM_LEGENDAS.get(user_id) and legenda_recebida:
        ALBUM_LEGENDAS[user_id] = legenda_recebida

    await editar_painel(
        update,
        context,
        texto_painel_album(len(midias)),
        finalizar_album_keyboard(),
    )

    return ALBUM


async def finalizar_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    user_id = query.from_user.id
    midias = ALBUM_MIDIAS.get(user_id, [])

    if len(midias) < 2:
        await query.answer(
            "O Ã¡lbum precisa ter pelo menos 2 mÃ­dias.",
            show_alert=True,
        )
        return ALBUM

    await query.answer()
    legenda_usuario = ALBUM_LEGENDAS.get(user_id, "")
    legenda_completa = montar_legenda_album(legenda_usuario)
    lista_envio = []

    for indice, item in enumerate(midias[:10]):
        legenda = legenda_completa if indice == 0 else None

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
        await editar_painel(
            update,
            context,
            "â ERRO AO ENVIAR ÃLBUM\n\n"
            f"{erro}\n\n"
            "Tente finalizar novamente ou cancele o processo.",
            finalizar_album_keyboard(),
        )
        return ALBUM

    adicionar_album(len(lista_envio))
    ALBUM_MIDIAS.pop(user_id, None)
    ALBUM_LEGENDAS.pop(user_id, None)

    await editar_painel(
        update,
        context,
        "â ÃLBUM ENVIADO\n\n"
        "O Ã¡lbum foi publicado com sucesso.\n\n"
        "Toque abaixo para apagar as mensagens usadas e voltar ao painel.",
        processo_finalizado_keyboard(),
    )

    return ConversationHandler.END


async def receber_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = update.effective_user.id

    if user_id not in AGUARDANDO_DIVULGACAO:
        await apagar_mensagem_segura(
            context.bot,
            update.effective_chat.id,
            update.effective_message.message_id,
        )
        await mostrar_painel_principal(update, context)
        return

    await registrar_mensagem_entrada(update)

    try:
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
            await editar_painel(
                update,
                context,
                "â ï¸ TIPO NÃO SUPORTADO\n\n"
                "Envie um texto, uma foto ou um vÃ­deo.",
                cancelar_processo_keyboard(),
            )
            return
    except Exception as erro:
        await editar_painel(
            update,
            context,
            "â ERRO AO ENVIAR DIVULGAÃÃO\n\n"
            f"{erro}\n\n"
            "Envie novamente ou cancele o processo.",
            cancelar_processo_keyboard(),
        )
        return

    AGUARDANDO_DIVULGACAO.discard(user_id)
    adicionar_envio(1)

    await editar_painel(
        update,
        context,
        "â DIVULGAÃÃO ENVIADA\n\n"
        "A publicaÃ§Ã£o foi enviada para o grupo.\n\n"
        "Toque abaixo para apagar as mensagens usadas e voltar ao painel.",
        processo_finalizado_keyboard(),
    )


async def apagar_mensagem_avulsa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return

    await apagar_mensagem_segura(
        context.bot,
        update.effective_chat.id,
        update.effective_message.message_id,
    )
    await mostrar_painel_principal(update, context)
