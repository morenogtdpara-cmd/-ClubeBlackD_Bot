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
# AGENDAMENTOS
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

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    await update.message.reply_text(

        "BOT ON ✅\n\nUse /divulgar, /d_album ou /agendar."

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

        albuns[grupo] = []

    if len(albuns[grupo]) < 10:

        albuns[grupo].append(mensagem)

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

    for item in albuns[grupo]:

        if item.photo:

            midias.append(

                InputMediaPhoto(

                    media=item.photo[-1].file_id,

                    caption=LEGENDA_FIXA.strip()
                    if len(midias) == 0
                    else None

                )

            )

        elif item.video:

            midias.append(

                InputMediaVideo(

                    media=item.video.file_id,

                    caption=LEGENDA_FIXA.strip()
                    if len(midias) == 0
                    else None

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

    # ==============================
    # ÁLBUM AGENDADO
    # ==============================

    if mensagem.media_group_id:

        grupo = mensagem.media_group_id

        if grupo not in albuns:

            await update.message.reply_text(

                "⚠️ Álbum não encontrado."

            )

            return

        midias_album = []

        for item in albuns[grupo]:

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

            "midias": midias_album

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

    # ==============================
    # PUBLICAÇÃO SOLO AGENDADA
    # ==============================

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

        print(

            "AGENDAMENTO ENCONTRADO:",

            item

        )

        if item["horario"] != agora:

            continue

        try:

            if item.get("tipo") == "album":

                midias = []

                for item_midia in item["midias"]:

                    if item_midia["tipo"] == "foto":

                        midias.append(

    InputMediaPhoto(

        item_midia["file_id"],

        LEGENDA_FIXA.strip()
        if len(midias) == 0
        else None

    )

)

                    elif item_midia["tipo"] == "video":

                        midias.append(

                            InputMediaVideo(

                                media=item_midia["file_id"],

                                caption=LEGENDA_FIXA.strip()
                                if len(midias) == 0
                                else None

                            )

                        )

                if midias:

                    await context.bot.send_media_group(

                        chat_id=GROUP_ID,

                        media=midias

                    )

                print("ÁLBUM ENVIADO ✅")

            else:

                # ==============================
                # SOLO AUTOMÁTICO
                # ==============================

                await context.bot.copy_message(

                    chat_id=GROUP_ID,

                    from_chat_id=item["chat_id"],

                    message_id=item["message_id"],

                    reply_markup=botoes_vip()

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
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand(
            "start",
            "BOT ON ✅"
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