import os
import asyncio
import json

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
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
# 🖤 BLACK SYSTEM
# ==============================

INICIO_BOT = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)


STATUS_SISTEMA = {

    "data": INICIO_BOT.strftime("%d/%m/%Y"),

    "envios_hoje": 0,

    "midias_hoje": 0,

    "feedbacks_hoje": 0,

    "ultimo_envio": None,

    "ultimo_tipo": None,

    "ultimo_status": None

}


def atualizar_dia():

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    data_atual = agora.strftime("%d/%m/%Y")


    if STATUS_SISTEMA["data"] != data_atual:

        STATUS_SISTEMA["data"] = data_atual

        STATUS_SISTEMA["envios_hoje"] = 0

        STATUS_SISTEMA["midias_hoje"] = 0

        STATUS_SISTEMA["feedbacks_hoje"] = 0



def registrar_envio(
    tipo,
    quantidade=1
):

    atualizar_dia()

    STATUS_SISTEMA["envios_hoje"] += 1

    STATUS_SISTEMA["midias_hoje"] += quantidade

    STATUS_SISTEMA["ultimo_envio"] = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).strftime("%H:%M")

    STATUS_SISTEMA["ultimo_tipo"] = tipo

    STATUS_SISTEMA["ultimo_status"] = "Sucesso"



# ==============================
# ⭐ FEEDBACK SYSTEM
# ==============================

ARQUIVO_FEEDBACKS = "feedbacks.json"


def carregar_feedbacks():

    if not Path(
        ARQUIVO_FEEDBACKS
    ).exists():

        return []


    with open(
        ARQUIVO_FEEDBACKS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)



def salvar_feedbacks(lista):

    with open(
        ARQUIVO_FEEDBACKS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            lista,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



feedbacks = carregar_feedbacks()


albuns = {}


# ==============================
# 📌 AGENDAMENTOS
# ==============================

ARQUIVO_AGENDAMENTOS = "agendamentos.json"


def carregar_agendamentos():

    if not Path(
        ARQUIVO_AGENDAMENTOS
    ).exists():

        return []


    with open(
        ARQUIVO_AGENDAMENTOS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)



def salvar_agendamentos(lista):

    with open(
        ARQUIVO_AGENDAMENTOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            lista,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


agendamentos = carregar_agendamentos()



# ==============================
# 🔥 BOTÃO VIP
# ==============================

def botoes_vip():

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



# ==============================
# 📝 LEGENDAS
# ==============================

LEGENDA_FIXA = """
🔥 CONTEÚDO EXCLUSIVO LIBERADO 🔥

🚀 Acesse nosso VIP:
@ClubeBlackBot
"""


LEGENDA_FEEDBACK = """
🖤 FEEDBACK REAL DE MEMBRO VIP

⭐ Membro satisfeito com o acesso

🔥 Conteúdo atualizado
💎 Acesso exclusivo
🚀 Entre para o VIP
"""



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

        "⚡ Sistema Ativo ⚡\n\n"

        "━━━━━━━━━━━\n\n"

        "📋 HOJE\n\n"

        f"👑 Envios: {STATUS_SISTEMA['envios_hoje']}/∞\n"

        f"📱 Mídias: {STATUS_SISTEMA['midias_hoje']}\n"

        f"⭐ Feedbacks: {STATUS_SISTEMA['feedbacks_hoje']}\n"

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Controle total\n"

        "⚡ Sistema protegido ⚡"

    )


# ==============================
# 📊 STATUS REAL
# ==============================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    atualizar_dia()


    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )


    tempo = agora - INICIO_BOT


    horas = tempo.seconds // 3600

    minutos = (tempo.seconds % 3600) // 60



    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        f"⚡ Sistema Ativo há: {horas}h {minutos}m\n\n"

        "━━━━━━━━━━━\n\n"

        "📋 HOJE\n\n"

        f"👑 Envios: {STATUS_SISTEMA['envios_hoje']}/∞\n"

        f"📱 Mídias: {STATUS_SISTEMA['midias_hoje']}\n"

        f"⭐ Feedbacks: {STATUS_SISTEMA['feedbacks_hoje']}\n"

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Sistema protegido ⚡"

    )



# ==============================
# 📸 RECEBER ÁLBUM
# ==============================

async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    mensagem = update.message


    if not mensagem.media_group_id:

        return


    grupo = mensagem.media_group_id


    if grupo not in albuns:

        albuns[grupo] = {

            "mensagens": [],

            "legenda": mensagem.caption or ""

        }



    if len(
        albuns[grupo]["mensagens"]
    ) < 10:

        albuns[grupo]["mensagens"].append(
            mensagem
        )


    if mensagem.caption:

        albuns[grupo]["legenda"] = mensagem.caption



# ==============================
# 📢 DIVULGAR NORMAL
# ==============================

async def divulgar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    if not update.message.reply_to_message:

        return


    mensagem = update.message.reply_to_message


    await context.bot.copy_message(

        chat_id=GROUP_ID,

        from_chat_id=mensagem.chat.id,

        message_id=mensagem.message_id,

        reply_markup=botoes_vip()

    )


    registrar_envio(
        "Publicação"
    )



# ==============================
# ⭐ CENTRAL DE FEEDBACKS
# ==============================

def botoes_feedback():

    return InlineKeyboardMarkup(

        [

            [

                InlineKeyboardButton(
                    "⚡ Envio Imediato",
                    callback_data="feedback_imediato"
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
                    callback_data="stats_feedback"
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



# ==============================
# /feedback - PAINEL
# ==============================

async def feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    disponiveis = len(

        [

            f for f in feedbacks

            if f.get("usado") == False

        ]

    )


    usados = len(

        [

            f for f in feedbacks

            if f.get("usado") == True

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



# ==============================
# ⚡ ENVIO IMEDIATO
# ==============================

async def enviar_feedback_imediato(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    if not update.message.reply_to_message:

        await update.message.reply_text(

            "⚠️ Responda uma FOTO para enviar."

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

        reply_markup=botoes_vip()

    )


    STATUS_SISTEMA["feedbacks_hoje"] += 1


    registrar_envio(

        "Feedback"

    )


    await update.message.reply_text(

        "✅ Feedback publicado!"

    )



# ==============================
# 📊 CALLBACK DOS BOTÕES
# ==============================

async def botoes_feedback_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if query.data == "feedback_imediato":

        await query.message.reply_text(

            "⚡ Envio Imediato\n\n"

            "Responda uma FOTO e use o botão novamente."

        )


    elif query.data == "stats_feedback":


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

            f"♻️ Usados: {usados}"

        )


    elif query.data == "reset_feedback":


        feedbacks.clear()

        salvar_feedbacks(

            feedbacks

        )


        await query.message.reply_text(

            "🔄 Feedbacks resetados!"

        )


    elif query.data == "adicionar_feedback":


        await query.message.reply_text(

            "➕ Adicionar Feedback\n\n"

            "Envie a FOTO que deseja salvar."

        )


    elif query.data == "agendar_feedback":


        await query.message.reply_text(

            "⏰ Agendar Feedback\n\n"

            "Use o horário desejado.\n"

            "Exemplo: 22:00"

        )


    else:


        await query.message.reply_text(

            "⚠️ Função não configurada."

        )



# ==============================
# 👑 VIP
# ==============================

async def entrarnovip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    await context.bot.send_message(

        chat_id=GROUP_ID,

        text="🔥 ENTRE NO VIP 🔥",

        reply_markup=botoes_vip()

    )



# ==============================
# 🤖 INICIAR BOT
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand(
            "start",
            "BLACK SYSTEM 👑"
        ),

        BotCommand(
            "status",
            "STATUS DO SISTEMA 🖤"
        ),

        BotCommand(
            "divulgar",
            "DIVULGAR 🔥"
        ),

        BotCommand(
            "d_album",
            "DIVULGAR ÁLBUM 🖼️"
        ),

        BotCommand(
            "feedback",
            "FEEDBACK VIP ⭐"
        ),

        BotCommand(
            "agendar",
            "AGENDAR DIVULGAÇÃO ⏰"
        )

    ]


    await app.bot.set_my_commands(
        comandos
    )



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
        "divulgar",
        divulgar
    )

)


app.add_handler(

    CommandHandler(
        "feedback",
        feedback
    )

)


app.add_handler(

    CallbackQueryHandler(
        botoes_feedback_callback
    )

)


app.add_handler(

    CommandHandler(
        "entrarnovip",
        entrarnovip
    )

)


app.add_handler(

    MessageHandler(

        filters.PHOTO | filters.VIDEO,

        receber_album

    )

)



print(

    "Bot iniciado ✅"

)



app.run_polling()