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
# LEGENDA FIXA
# ==============================

LEGENDA_FIXA = """
🔥 CONTEÚDO EXCLUSIVO LIBERADO 🔥

🚀 Acesse nosso canal oficial:
@ClubeBlackBot
"""

albuns = {}

# ==============================
# AGENDAMENTO AUTOMÁTICO
# ==============================

ARQUIVO_AGENDAMENTOS = "agendamentos.json"

def carregar_agendamentos():

    if not Path(ARQUIVO_AGENDAMENTOS).exists():
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

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 ENTRAR NO VIP 🔥",
                url=VIP_LINK
            )
        ]
    ])

# ==============================
# START
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "BOT ON ✅\n\nUse /divulgar, /d_album ou /agendar."
    )

# ==============================
# DIVULGAR
# ==============================

async def divulgar(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

# ==============================
# RECEBER ÁLBUM
# ==============================

async def receber_album(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    mensagem = update.message

    if not mensagem.media_group_id:
        return

    grupo = mensagem.media_group_id

    if grupo not in albuns:
        albuns[grupo] = []

    albuns[grupo].append(mensagem)

    await asyncio.sleep(3)

# ==============================
# DIVULGAR ÁLBUM
# ==============================

async def d_album(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    texto = ""

    for item in albuns[grupo]:

        if item.caption:

            texto = item.caption.strip()
            break

    if texto:

        legenda = (
            texto
            + "\n\n"
            + LEGENDA_FIXA.strip()
        )

    else:

        legenda = LEGENDA_FIXA.strip()

    midias = []

    for i, item in enumerate(albuns[grupo]):

        if item.photo:

            midias.append(
                InputMediaPhoto(
                    media=item.photo[-1].file_id,
                    caption=legenda if i == 0 else None
                )
            )

        elif item.video:

            midias.append(
                InputMediaVideo(
                    media=item.video.file_id,
                    caption=legenda if i == 0 else None
                )
            )

    if midias:

        await context.bot.send_media_group(
            chat_id=GROUP_ID,
            media=midias
        )

    del albuns[grupo]

    await update.message.reply_text(
        "✅ Álbum divulgado!"
    )

# ==============================
# AGENDAR PUBLICAÇÃO
# ==============================

async def agendar_publicacao(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    agendamentos.append({

        "horario": horario,
        "chat_id": mensagem.chat.id,
        "message_id": mensagem.message_id

    })
    salvar_agendamentos(agendamentos)
    print("AGENDAMENTOS SALVOS:", agendamentos)

    await update.message.reply_text(
        f"✅ Agendado para {horario}"
    )

# ==============================
# VERIFICAR AGENDAMENTOS
# ==============================

async def verificar_agendamentos(
    context: ContextTypes.DEFAULT_TYPE
):

    print("VERIFICANDO AGENDAMENTOS")

    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M")
    
    print("HORA ATUAL:", agora)
    print("LISTA DE AGENDAMENTOS:", agendamentos)
    for item in agendamentos.copy():

        if item["horario"] == agora:

            try:

                await context.bot.copy_message(

                    chat_id=GROUP_ID,

                    from_chat_id=item["chat_id"],

                    message_id=item["message_id"],

                    reply_markup=botoes_vip()

                )

                print("PUBLICAÇÃO ENVIADA ✅")

                agendamentos.remove(item)

                salvar_agendamentos(
                    agendamentos
                )

            except Exception as e:

                print(
                    "ERRO AO ENVIAR PUBLICAÇÃO:",
                    e
                )
    print("VERIFICANDO AGENDAMENTOS")
    agora = datetime.now().strftime("%H:%M")

    enviados = []

    for item in agendamentos.copy():

        if item["horario"] == agora:

            await context.bot.copy_message(

                chat_id=GROUP_ID,

                from_chat_id=item["chat_id"],

                message_id=item["message_id"],

                reply_markup=botoes_vip()

            )

            enviados.append(item)

    for item in enviados:

        agendamentos.remove(item)

    if enviados:

        salvar_agendamentos(
            agendamentos
        )

# ==============================
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand("start", "BOT ON ✅"),
        BotCommand("divulgar", "DIVULGAR 🔥"),
        BotCommand("d_album", "DIVULGAR ÁLBUM 🖼️"),
        BotCommand("entrarnovip", "BOTÃO VIP"),
        BotCommand("agendar", "AGENDAR DIVULGAÇÃO ⏰")

    ]

    await app.bot.set_my_commands(
        comandos
    )

# ==============================
# VIP
# ==============================

async def entrarnovip(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
print(app.job_queue)
app.job_queue.run_repeating(

    verificar_agendamentos,

    interval=30,

    first=10

)

print("Bot iniciado ✅")

app.run_polling()