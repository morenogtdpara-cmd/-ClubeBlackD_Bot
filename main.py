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
# LEGENDA FIXA DO ÁLBUM
# ==============================

LEGENDA_FIXA = """
🔥 ACESSE NOSSO CANAL OFICIAL DE VENDAS:
@ClubeBlackBot
"""

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
        "BOT ON ✅\n\nUse /divulgar ou /d_album."
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

    legenda = ""

    if mensagem.caption:
        legenda = mensagem.caption

    await context.bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=mensagem.chat.id,
        message_id=mensagem.message_id,
        caption=legenda if legenda else None,
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
        return

    grupo = update.message.reply_to_message.media_group_id

    if not grupo or grupo not in albuns:
        await update.message.reply_text(
            "⚠️ Álbum não encontrado."
        )
        return

    texto = update.message.text.replace("/d_album", "").strip()

    if texto:
        legenda = texto + "\n\n" + LEGENDA_FIXA.strip()
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

    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=midias
    )

    del albuns[grupo]

    await update.message.reply_text(
        "✅ Álbum divulgado!"
    )

# ==============================
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand("start", "BOT ON ✅"),
        BotCommand("divulgar", "DIVULGAR 🔥"),
        BotCommand("d_album", "DIVULGAR ÁLBUM 🖼️")

    ]

    await app.bot.set_my_commands(comandos)

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

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("divulgar", divulgar))

app.add_handler(CommandHandler("d_album", d_album))

app.add_handler(CommandHandler("entrarnovip", entrarnovip))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO,
        receber_album
    )
)

print("Bot iniciado ✅")

app.run_polling()