from telegram import Update
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from database import (
    listar_mensagens_temporarias,
    pegar_painel,
    pegar_relatorio,
    registrar_mensagem_temporaria,
    remover_mensagem_temporaria,
    salvar_painel,
)
from fila import pegar_fila
from keyboards import painel_keyboard


def texto_painel_principal():
    envios, midias, albuns, _ = pegar_relatorio()
    programadas = len(pegar_fila())

    return (
        "🥷🏾 BLACK PRIVATE\n\n"
        "⚜️ CENTRAL DE OPERAÇÕES\n\n"
        "📊 RESUMO DO DIA\n"
        f"📤 Envios: {envios}/30\n"
        f"📱 Mídias: {midias}\n"
        f"🖼️ Álbuns: {albuns}\n"
        f"⏰ Programadas: {programadas}\n\n"
        "Selecione um serviço:"
    )


async def apagar_mensagem_segura(bot, chat_id, message_id):
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        return True

    except BadRequest as erro:
        texto_erro = str(erro).lower()

        if (
            "message to delete not found" in texto_erro
            or "message not found" in texto_erro
        ):
            return True

        return False

    except TelegramError:
        return False


async def registrar_mensagem_entrada(update: Update):
    mensagem = update.effective_message

    if not mensagem:
        return

    chat_id = mensagem.chat_id
    painel_id = pegar_painel(chat_id)

    if mensagem.message_id != painel_id:
        registrar_mensagem_temporaria(
            chat_id,
            mensagem.message_id,
        )


async def limpar_mensagens_temporarias(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
):
    painel_id = pegar_painel(chat_id)
    mensagens = listar_mensagens_temporarias(chat_id)

    for message_id in mensagens:
        if message_id == painel_id:
            remover_mensagem_temporaria(
                chat_id,
                message_id,
            )
            continue

        apagada = await apagar_mensagem_segura(
            context.bot,
            chat_id,
            message_id,
        )

        if apagada:
            remover_mensagem_temporaria(
                chat_id,
                message_id,
            )


async def editar_painel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    texto: str,
    reply_markup=None,
):
    chat = update.effective_chat

    if not chat:
        return None

    chat_id = chat.id
    painel_id = pegar_painel(chat_id)
    query = update.callback_query

    if query and query.message:
        mensagem_clicada_id = query.message.message_id

        if painel_id != mensagem_clicada_id:
            if painel_id:
                await apagar_mensagem_segura(
                    context.bot,
                    chat_id,
                    painel_id,
                )

            painel_id = mensagem_clicada_id
            salvar_painel(
                chat_id,
                painel_id,
            )

    if painel_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=painel_id,
                text=texto,
                reply_markup=reply_markup,
            )
            return painel_id

        except BadRequest as erro:
            if "message is not modified" in str(erro).lower():
                return painel_id

        except TelegramError:
            pass

        painel_apagado = await apagar_mensagem_segura(
            context.bot,
            chat_id,
            painel_id,
        )

        if not painel_apagado:
            return painel_id

    nova_mensagem = await context.bot.send_message(
        chat_id=chat_id,
        text=texto,
        reply_markup=reply_markup,
    )

    salvar_painel(
        chat_id,
        nova_mensagem.message_id,
    )

    return nova_mensagem.message_id


async def mostrar_painel_principal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    return await editar_painel(
        update,
        context,
        texto_painel_principal(),
        painel_keyboard(),
    )