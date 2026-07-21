from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import ADMIN_ID, GROUP_ID, VIP_LINK
from keyboards import (
    cancelar_processo_keyboard,
    processo_finalizado_keyboard,
    vip_keyboard,
)
from painel import editar_painel, registrar_mensagem_entrada


FEEDBACK = 2


LEGENDA_FEEDBACK = """
⭐ FEEDBACK REAL ⭐️

Mais um cliente satisfeito.

Quer ter acesso ao conteúdo completo?

💦 Faça parte você também.
"""


async def abrir_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "Acesso não autorizado.",
            show_alert=True,
        )
        return ConversationHandler.END

    await query.answer()

    await editar_painel(
        update,
        context,
        "⭐ FEEDBACK ATIVADO\n\n"
        "📸 Envie a foto.",
        cancelar_processo_keyboard(),
    )

    return FEEDBACK


async def receber_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    await registrar_mensagem_entrada(update)

    if not update.message.photo:
        await editar_painel(
            update,
            context,
            "⚠️ FORMATO INVÁLIDO\n\n"
            "Envie uma foto para publicar como feedback.",
            cancelar_processo_keyboard(),
        )
        return FEEDBACK

    try:
        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=LEGENDA_FEEDBACK,
            reply_markup=vip_keyboard(VIP_LINK),
        )
    except Exception as erro:
        await editar_painel(
            update,
            context,
            "❌ ERRO AO ENVIAR FEEDBACK\n\n"
            f"{erro}\n\n"
            "Envie a foto novamente ou cancele o processo.",
            cancelar_processo_keyboard(),
        )
        return FEEDBACK

    await editar_painel(
        update,
        context,
        "✅ FEEDBACK ENVIADO\n\n"
        "Toque abaixo para apagar as mensagens usadas e voltar ao painel.",
        processo_finalizado_keyboard(),
    )

    return ConversationHandler.END
