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
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -1004231485932

OWNER_ID = 8880948641

VIP_LINK = "https://t.me/ClubeBlackBot"

# ==============================
# 🖤 BLACK SYSTEM - DADOS REAIS
# ==============================

INICIO_BOT = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

STATUS_SISTEMA = {

    "data": INICIO_BOT.strftime("%d/%m/%Y"),

    "envios_hoje": 0,

    "midias_hoje": 0,

    "ultimo_envio": None,

    "ultimo_tipo": None,

    "ultimo_status": None

}

def atualizar_dia():

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    data_atual = agora.strftime(
        "%d/%m/%Y"
    )

    if STATUS_SISTEMA["data"] != data_atual:

        STATUS_SISTEMA["data"] = data_atual

        STATUS_SISTEMA["envios_hoje"] = 0

        STATUS_SISTEMA["midias_hoje"] = 0

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
# LEGENDA FIXA
# ==============================

LEGENDA_FIXA = """
🔥 CONTEÚDO EXCLUSIVO LIBERADO 🔥

🚀 Acesse nosso canal oficial:
@ClubeBlackBot
"""

albuns = {}
# ==============================
# FEEDBACKS
# ==============================

ARQUIVO_FEEDBACKS = "feedbacks.json"

def carregar_feedbacks():

    if not Path(ARQUIVO_FEEDBACKS).exists():

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

aguardando_feedback = set()
# ==============================
# AGENDAMENTOS
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
# BOTÃO VIP
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
# START
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

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Controle total\n"

        "⚡ Sistema protegido ⚡"

    )

# ==============================
# STATUS REAL
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

    proximo = "--:--"

    if agendamentos:

        horarios = sorted(

            [

                item["horario"]

                for item in agendamentos

            ]

        )

        proximo = horarios[0]

    ultimo = (

        STATUS_SISTEMA["ultimo_envio"]

        or "--:--"

    )

    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        "👑 Bem-vindo de volta, Chefe! 🥷🏾\n\n"

        f"⚡ Sistema Ativo há: {horas}h {minutos}m\n\n"

        "━━━━━━━━━━━\n\n"

        "📋 HOJE\n\n"

        f"👑 Envios: {STATUS_SISTEMA['envios_hoje']}/∞\n"

        f"📱 Mídias: {STATUS_SISTEMA['midias_hoje']}\n"

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "⚡ PRÓXIMA DIVULGAÇÃO\n\n"

        f"🕙 {proximo}\n"

        "📢 Publicação\n\n"

        "━━━━━━━━━━━\n\n"

        "📌 ÚLTIMO ENVIO\n\n"

        f"🕘 {ultimo}\n"

        f"✅ {STATUS_SISTEMA['ultimo_status'] or '--'}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Controle total\n"

        "⚡ Sistema protegido ⚡"

    )

# ==============================
# RECEBER ÁLBUM
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

    if len(albuns[grupo]["mensagens"]) < 10:

        albuns[grupo]["mensagens"].append(
            mensagem
        )

    if mensagem.caption:

        albuns[grupo]["legenda"] = mensagem.caption

    await asyncio.sleep(3)

# ==============================
# DIVULGAR
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
# DIVULGAR ÁLBUM MANUAL
# ==============================

async def d_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        return

    grupo = update.message.reply_to_message.media_group_id

    if not grupo or grupo not in albuns:

        await update.message.reply_text(

            "⚠️ Álbum não encontrado."

        )

        return

    midias = []

    legenda_usuario = albuns[grupo].get(

        "legenda",

        ""

    )

    if legenda_usuario:

        legenda_final = (

            legenda_usuario.strip()

            + "\n\n"

            + LEGENDA_FIXA.strip()

        )

    else:

        legenda_final = LEGENDA_FIXA.strip()

    for item in albuns[grupo]["mensagens"]:

        if item.photo:

            midias.append(

                InputMediaPhoto(

                    media=item.photo[-1].file_id,

                    caption=legenda_final

                    if len(midias) == 0

                    else None

                )

            )

        elif item.video:

            midias.append(

                InputMediaVideo(

                    media=item.video.file_id,

                    caption=legenda_final

                    if len(midias) == 0

                    else None

                )

            )

    if midias:

        await context.bot.send_media_group(

            chat_id=GROUP_ID,

            media=midias

        )

    registrar_envio(

        "Álbum",

        len(midias)

    )

    del albuns[grupo]

    await update.message.reply_text(

        "✅ Álbum divulgado!"

    )

# ==============================
# AGENDAR PUBLICAÇÃO
# ==============================

async def agendar_publicacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        await update.message.reply_text(

            "⚠️ Responda a publicação e use /agendar HH:MM"

        )

        return

    if not context.args:

        await update.message.reply_text(

            "⚠️ Exemplo: /agendar 08:00"

        )

        return

    horario = context.args[0]

    try:

        datetime.strptime(

            horario,

            "%H:%M"

        )

    except:

        await update.message.reply_text(

            "⚠️ Horário inválido."

        )

        return

    mensagem = update.message.reply_to_message

    if mensagem.media_group_id:

        grupo = mensagem.media_group_id

        if grupo not in albuns:

            await update.message.reply_text(

                "⚠️ Álbum não encontrado."

            )

            return

        midias_album = []

        for item in albuns[grupo]["mensagens"]:

            if item.photo:

                midias_album.append({

                    "tipo": "foto",

                    "file_id": item.photo[-1].file_id

                })

            elif item.video:

                midias_album.append({

                    "tipo": "video",

                    "file_id": item.video.file_id

                })

        agendamentos.append({

            "horario": horario,

            "tipo": "album",

            "chat_id": GROUP_ID,

            "midias": midias_album,

            "legenda": albuns[grupo].get(

                "legenda",

                ""

            )

        })

        salvar_agendamentos(

            agendamentos

        )

        await update.message.reply_text(

            f"✅ Álbum agendado com sucesso!\n\n"

            f"📅 Horário: {horario}\n"

            f"🖼️ Tipo: Álbum"

        )

        return

    agendamentos.append({

        "horario": horario,

        "tipo": "publicacao",

        "chat_id": mensagem.chat.id,

        "message_id": mensagem.message_id

    })

    salvar_agendamentos(

        agendamentos

    )

    await update.message.reply_text(

        f"✅ Agendado com sucesso!\n\n"

        f"📅 Horário: {horario}\n"

        f"📢 Tipo: Publicação"

    )

# ==============================
# VERIFICAR AGENDAMENTOS
# ==============================

async def verificar_agendamentos(
    context: ContextTypes.DEFAULT_TYPE
):

    print("VERIFICANDO AGENDAMENTOS")

    agora = datetime.now(

        ZoneInfo("America/Sao_Paulo")

    ).strftime("%H:%M")

    for item in agendamentos.copy():

        if item["horario"] != agora:

            continue

        try:

            if item.get("tipo") == "album":

                midias = []

                legenda_usuario = item.get(

                    "legenda",

                    ""

                )

                if legenda_usuario:

                    legenda_final = (

                        legenda_usuario.strip()

                        + "\n\n"

                        + LEGENDA_FIXA.strip()

                    )

                else:

                    legenda_final = LEGENDA_FIXA.strip()

                for item_midia in item["midias"]:

                    if item_midia["tipo"] == "foto":

                        midias.append(

                            InputMediaPhoto(

                                media=item_midia["file_id"],

                                caption=legenda_final

                                if len(midias) == 0

                                else None

                            )

                        )

                    elif item_midia["tipo"] == "video":

                        midias.append(

                            InputMediaVideo(

                                media=item_midia["file_id"],

                                caption=legenda_final

                                if len(midias) == 0

                                else None

                            )

                        )

                if midias:

                    await context.bot.send_media_group(

                        chat_id=GROUP_ID,

                        media=midias

                    )

                registrar_envio(

                    "Álbum",

                    len(midias)

                )

                print("ÁLBUM ENVIADO ✅")

            else:

                await context.bot.copy_message(

                    chat_id=GROUP_ID,

                    from_chat_id=item["chat_id"],

                    message_id=item["message_id"],

                    reply_markup=botoes_vip()

                )

                registrar_envio(

                    "Publicação"

                )

                print("PUBLICAÇÃO ENVIADA ✅")

            await context.bot.send_message(

                chat_id=OWNER_ID,

                text=(

                    "✅ Publicação enviada com sucesso!\n\n"

                    f"📅 Horário: {agora}\n"

                    f"📢 Tipo: {item.get('tipo', 'publicacao')}"

                )

            )

            agendamentos.remove(item)

            salvar_agendamentos(

                agendamentos

            )

        except Exception as e:

            print(

                "ERRO AO ENVIAR AGENDAMENTO:",

                e

            )
# ==============================
# FEEDBACK
# ==============================

async def feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    await update.message.reply_text(

        "📝 Sistema de Feedback carregado."

    )
# ==============================
# MENU
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

            "agendar",

            "AGENDAR DIVULGAÇÃO ⏰"

        )

    ]

    await app.bot.set_my_commands(

        comandos

    )

# ==============================
# VIP
# ==============================

async def entrarnovip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    await context.bot.send_message(

        chat_id=GROUP_ID,

        text="",

        reply_markup=botoes_vip()

    )

# ==============================
# BOT
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

        "divulgar",

        divulgar

    )

)

app.add_handler(

    CommandHandler(

        "d_album",

        d_album

    )

)

app.add_handler(

    CommandHandler(

        "entrarnovip",

        entrarnovip

    )

)

app.add_handler(

    CommandHandler(

        "agendar",

        agendar_publicacao

    )

)

app.add_handler(

    MessageHandler(

        filters.PHOTO | filters.VIDEO,

        receber_album

    )

)

app.job_queue.run_repeating(

    verificar_agendamentos,

    interval=30,

    first=10

)

print("Bot iniciado ✅")

app.run_polling()