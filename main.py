import os
import asyncio

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
# MENSAGENS PERSONALIZADAS
# ==============================

MENSAGENS = {
    1: "🔥 NOVO CONTEÚDO LIBERADO 🔥\n\nConfira agora!",
    2: "🚀 NOVIDADE CHEGANDO!\n\nAcesse agora!",
    3: "💎 Conteúdo especial disponível."
}

mensagem_atual = 1

albuns = {}

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
        "BOT ON ✅\n\nUse /divulgar ou /d_album para enviar uma postagem."
    )

# ==============================
# ESCOLHER MENSAGEM
# ==============================

async def escolher_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mensagem_atual

    if update.effective_user.id != OWNER_ID:
        return

    comando = update.message.text.replace("/mensagem", "")

    if comando.isdigit():

        numero = int(comando)

        if numero in MENSAGENS:

            mensagem_atual = numero

            await update.message.reply_text(
                f"✅ Mensagem {numero} selecionada!"
            )

        else:

            await update.message.reply_text(
                "⚠️ Essa mensagem não existe."
            )

# ==============================
# ENTRAR VIP
# ==============================

async def entrarvip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        f"🔥 ENTRAR NO VIP 🔥\n\n{VIP_LINK}"
    )

# ==============================
# DIVULGAR
# ==============================

async def divulgar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Responda uma foto ou vídeo usando /divulgar."
        )
        return

    mensagem = update.message.reply_to_message

    legenda = MENSAGENS[mensagem_atual]

    if mensagem.caption:

        legenda += "\n\n" + mensagem.caption

    await context.bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=mensagem.chat.id,
        message_id=mensagem.message_id,
        caption=legenda,
        reply_markup=botoes_vip()
    )

    await update.message.reply_text(
        "✅ Divulgação enviada!"
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

        await update.message.reply_text(
            "⚠️ Responda o álbum usando /d_album."
        )
        return

    grupo = update.message.reply_to_message.media_group_id

    if not grupo or grupo not in albuns:

        await update.message.reply_text(
            "⚠️ Álbum não encontrado. Envie o álbum, aguarde alguns segundos e tente novamente."
        )
        return

    legenda = MENSAGENS[mensagem_atual]

    legenda_manual = ""

    for item in albuns[grupo]:

        if item.caption:

            legenda_manual = item.caption

            break

    if legenda_manual:

        legenda += "\n\n" + legenda_manual

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

    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=midias
    )

    del albuns[grupo]

    await update.message.reply_text(
        "✅ Álbum divulgado!"
    )

# ==============================
# CONFIGURAR MENU
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
            "mensagem1",
            "Usar mensagem 1"
        ),

        BotCommand(
            "mensagem2",
            "Usar mensagem 2"
        ),

        BotCommand(
            "mensagem3",
            "Usar mensagem 3"
        ),

        BotCommand(
            "entrarvip",
            "🔥 ENTRAR NO VIP 🔥"
        )
    ]

    await app.bot.set_my_commands(comandos)

# ==============================
# CRIAR BOT
# ==============================

app = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .post_init(configurar_menu)
    .build()
)

# ==============================
# COMANDOS
# ==============================

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
        "entrarvip",
        entrarvip
    )
)

# ==============================
# MENSAGENS 1, 2, 3
# ==============================

app.add_handler(
    MessageHandler(
        filters.Regex("^/mensagem[0-9]+$"),
        escolher_mensagem
    )
)

# ==============================
# RECEBER MÍDIAS
# ==============================

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO,
        receber_album
    )
)

print("Bot iniciado ✅")

app.run_polling()