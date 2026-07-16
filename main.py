import os
import json

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -1004231485932

OWNER_ID = 8880948641

VIP_LINK = "https://t.me/ClubeBlackBot"

# ==============================
# 🖤 SISTEMA
# ==============================

INICIO_BOT = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

STATUS_SISTEMA = {

    "data": INICIO_BOT.strftime("%d/%m/%Y"),

    "feedbacks_hoje": 0

}

def atualizar_dia():

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    data = agora.strftime(
        "%d/%m/%Y"
    )

    if STATUS_SISTEMA["data"] != data:

        STATUS_SISTEMA["data"] = data

        STATUS_SISTEMA["feedbacks_hoje"] = 0

# ==============================
# ⭐ FEEDBACKS
# ==============================

ARQUIVO_FEEDBACKS = "feedbacks.json"

ARQUIVO_AGENDADOS_FEEDBACK = "feedbacks_agendados.json"

def carregar_json(
    arquivo
):

    if not Path(arquivo).exists():

        return []

    try:

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []

def salvar_json(
    arquivo,
    dados
):

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )

feedbacks = carregar_json(
    ARQUIVO_FEEDBACKS
)

feedbacks_agendados = carregar_json(
    ARQUIVO_AGENDADOS_FEEDBACK
)

modo_feedback = {}

def botao_vip():

    return InlineKeyboardMarkup(

        [

            [

                InlineKeyboardButton(

                    "🔥 ENTRAR NO VIP 🔥",

                    url=VIP_LINK

                )

            ]

        ]

    )

LEGENDA_FEEDBACK = """
🖤 FEEDBACK REAL DE MEMBRO VIP

⭐ Membro satisfeito com o acesso

🔥 Conteúdo atualizado
💎 Acesso exclusivo
🚀 Entre para o VIP
"""

def botoes_feedback():

    return InlineKeyboardMarkup(

        [

            [

                InlineKeyboardButton(
                    "⚡ Envio Imediato",
                    callback_data="envio_imediato"
                )

            ],

            [

                InlineKeyboardButton(
                    "➕ Adicionar Feedback",
                    callback_data="adicionar_feedback"
                )

            ],

            [

                InlineKeyboardButton(
                    "⏰ Agendar Feedback",
                    callback_data="agendar_feedback"
                )

            ],

            [

                InlineKeyboardButton(
                    "📊 Estatísticas",
                    callback_data="estatisticas_feedback"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔄 Resetar Feedbacks",
                    callback_data="reset_feedback"
                )

            ]

        ]

    )

async def feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    disponiveis = len(

        [

            f for f in feedbacks

            if not f.get("usado")

        ]

    )

    usados = len(

        [

            f for f in feedbacks

            if f.get("usado")

        ]

    )

    await update.message.reply_text(

        "⭐ SISTEMA DE FEEDBACKS\n\n"

        f"📦 Total: {len(feedbacks)}\n"

        f"✅ Disponíveis: {disponiveis}\n"

        f"♻️ Usados: {usados}\n\n"

        "━━━━━━━━━━━",

        reply_markup=botoes_feedback()

    )

async def salvar_feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    if modo_feedback.get("acao") != "adicionar":

        return

    if not update.message.photo:

        return

    feedbacks.append(

        {

            "file_id": update.message.photo[-1].file_id,

            "usado": False

        }

    )

    salvar_json(

        ARQUIVO_FEEDBACKS,

        feedbacks

    )

    modo_feedback.clear()

    await update.message.reply_text(

        "✅ Feedback salvo!"

    )

# ==============================
# ⚡ ENVIO IMEDIATO
# ==============================

async def enviar_feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        await update.message.reply_text(

            "⚠️ Responda uma FOTO."

        )

        return

    mensagem = update.message.reply_to_message

    if not mensagem.photo:

        await update.message.reply_text(

            "⚠️ Apenas fotos."

        )

        return

    await context.bot.send_photo(

        chat_id=GROUP_ID,

        photo=mensagem.photo[-1].file_id,

        caption=LEGENDA_FEEDBACK,

        reply_markup=botao_vip()

    )

    STATUS_SISTEMA["feedbacks_hoje"] += 1

    await update.message.reply_text(

        "✅ Feedback publicado!"

    )

# ==============================
# ⚡ MODO ENVIO IMEDIATO PELO BOTÃO
# ==============================

async def receber_feedback_imediato(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    if modo_feedback.get("acao") != "imediato":

        return

    if not update.message.photo:

        return

    await context.bot.send_photo(

        chat_id=GROUP_ID,

        photo=update.message.photo[-1].file_id,

        caption=LEGENDA_FEEDBACK,

        reply_markup=botao_vip()

    )

    STATUS_SISTEMA["feedbacks_hoje"] += 1

    modo_feedback.clear()

    await update.message.reply_text(

        "✅ Feedback publicado!"

    )

async def receber_horario_feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    if modo_feedback.get("acao") != "agendar":

        return

    horario = update.message.text.strip()

    try:

        datetime.strptime(

            horario,

            "%H:%M"

        )

    except:

        await update.message.reply_text(

            "⚠️ Horário inválido.\nExemplo: 22:00"

        )

        return

    disponivel = None

    for item in feedbacks:

        if not item.get("usado"):

            disponivel = item

            break

    if not disponivel:

        await update.message.reply_text(

            "⚠️ Nenhum feedback disponível."

        )

        modo_feedback.clear()

        return

    feedbacks_agendados.append(

        {

            "horario": horario,

            "file_id": disponivel["file_id"]

        }

    )

    disponivel["usado"] = True

    salvar_json(

        ARQUIVO_FEEDBACKS,

        feedbacks

    )

    salvar_json(

        ARQUIVO_AGENDADOS_FEEDBACK,

        feedbacks_agendados

    )

    modo_feedback.clear()

    await update.message.reply_text(

        "✅ Feedback agendado!\n\n"

        f"⏰ Horário: {horario}"

    )

# ==============================
# 📊 CALLBACKS PAINEL
# ==============================

async def callback_feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    query = update.callback_query

    if update.effective_user.id != OWNER_ID:

        await query.answer()

        return

    await query.answer()

    if query.data == "adicionar_feedback":

        modo_feedback["acao"] = "adicionar"

        await query.message.reply_text(

            "➕ Envie a foto do feedback."

        )

    elif query.data == "agendar_feedback":

        modo_feedback["acao"] = "agendar"

        await query.message.reply_text(

            "⏰ Envie o horário.\n\n"

            "Exemplo: 22:00"

        )

    elif query.data == "envio_imediato":

        modo_feedback["acao"] = "imediato"

        await query.message.reply_text(

            "⚡ Envio Imediato ativado.\n\n"

            "Envie a FOTO agora."

        )

    elif query.data == "estatisticas_feedback":

        disponiveis = len(

            [

                f for f in feedbacks

                if not f.get("usado")

            ]

        )

        usados = len(

            [

                f for f in feedbacks

                if f.get("usado")

            ]

        )

        await query.message.reply_text(

            "📊 ESTATÍSTICAS\n\n"

            f"📦 Total: {len(feedbacks)}\n"

            f"✅ Disponíveis: {disponiveis}\n"

            f"♻️ Usados: {usados}\n"

            f"⏰ Agendados: {len(feedbacks_agendados)}"

        )

    elif query.data == "reset_feedback":

        feedbacks.clear()

        feedbacks_agendados.clear()

        salvar_json(

            ARQUIVO_FEEDBACKS,

            feedbacks

        )

        salvar_json(

            ARQUIVO_AGENDADOS_FEEDBACK,

            feedbacks_agendados

        )

        await query.message.reply_text(

            "🔄 Feedbacks resetados!"

        )

async def verificar_feedbacks_agendados(

    context: ContextTypes.DEFAULT_TYPE

):

    agora = datetime.now(

        ZoneInfo("America/Sao_Paulo")

    ).strftime("%H:%M")

    for item in feedbacks_agendados.copy():

        if item["horario"] != agora:

            continue

        try:

            await context.bot.send_photo(

                chat_id=GROUP_ID,

                photo=item["file_id"],

                caption=LEGENDA_FEEDBACK,

                reply_markup=botao_vip()

            )

            STATUS_SISTEMA["feedbacks_hoje"] += 1

            feedbacks_agendados.remove(

                item

            )

            salvar_json(

                ARQUIVO_AGENDADOS_FEEDBACK,

                feedbacks_agendados

            )

            await context.bot.send_message(

                chat_id=OWNER_ID,

                text=(

                    "✅ Feedback enviado!\n\n"

                    f"⏰ Horário: {agora}\n"

                    "⭐ Tipo: Feedback"

                )

            )

        except Exception as erro:

            print(

                "ERRO FEEDBACK AGENDADO:",

                erro

            )

# ==============================
# ▶️ START
# ==============================

async def start(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        "👑 Bem-vindo de volta, Chefe! 🥷🏾\n\n"

        "⭐ Sistema de Feedback Ativo\n\n"

        "━━━━━━━━━━━\n\n"

        f"⭐ Feedbacks: {len(feedbacks)}\n"

        f"⏰ Agendados: {len(feedbacks_agendados)}\n\n"

        "━━━━━━━━━━━\n\n"

        "⚡ Sistema protegido"

    )

# ==============================
# 📊 STATUS
# ==============================

async def status(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    if update.effective_user.id != OWNER_ID:

        return

    atualizar_dia()

    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        "📊 STATUS\n\n"

        f"⭐ Feedbacks hoje: {STATUS_SISTEMA['feedbacks_hoje']}\n"

        f"📦 Salvos: {len(feedbacks)}\n"

        f"⏰ Agendados: {len(feedbacks_agendados)}"

    )

async def comando_enviar_feedback(

    update: Update,

    context: ContextTypes.DEFAULT_TYPE

):

    await enviar_feedback(

        update,

        context

    )

# ==============================
# 🤖 CONFIGURAÇÃO MENU
# ==============================

async def configurar_menu(

    app

):

    comandos = [

        BotCommand(

            "start",

            "BLACK SYSTEM 👑"

        ),

        BotCommand(

            "status",

            "STATUS 🖤"

        ),

        BotCommand(

            "feedback",

            "PAINEL DE FEEDBACK ⭐"

        ),

        BotCommand(

            "enviar_feedback",

            "ENVIAR FEEDBACK ⚡"

        )

    ]

    await app.bot.set_my_commands(

        comandos

    )

# ==============================
# 🚀 APLICAÇÃO
# ==============================

app = (

    Application

    .builder()

    .token(BOT_TOKEN)

    .post_init(configurar_menu)

    .build()

)

app.add_handler(

    CommandHandler(

        "start",

        start

    )

)

app.add_handler(

    CommandHandler(

        "status",

        status

    )

)

app.add_handler(

    CommandHandler(

        "feedback",

        feedback

    )

)

app.add_handler(

    CommandHandler(

        "enviar_feedback",

        comando_enviar_feedback

    )

)

app.add_handler(

    CallbackQueryHandler(

        callback_feedback

    )

)

app.add_handler(

    MessageHandler(

        filters.PHOTO,

        receber_feedback_imediato

    )

)

app.add_handler(

    MessageHandler(

        filters.PHOTO,

        salvar_feedback

    )

)

app.add_handler(

    MessageHandler(

        filters.TEXT & ~filters.COMMAND,

        receber_horario_feedback

    )

)

app.job_queue.run_repeating(

    verificar_feedbacks_agendados,

    interval=30,

    first=10

)

# ==============================
# 🛡️ PROTEÇÃO FINAL
# ==============================

async def erro_global(

    update: object,

    context: ContextTypes.DEFAULT_TYPE

):

    print(

        "ERRO NO BOT:",

        context.error

    )

app.add_error_handler(

    erro_global

)

print(

    "🖤 BLACK SYSTEM ONLINE ✅"

)

app.run_polling()