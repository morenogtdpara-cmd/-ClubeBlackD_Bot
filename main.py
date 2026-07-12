import os
import json
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
# BANCO DE MENSAGENS
# ==============================

ARQUIVO_MENSAGENS = "mensagens.json"

def carregar_mensagens():

    try:
        with open(
            ARQUIVO_MENSAGENS,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except:

        return {}

def salvar_mensagens():

    with open(
        ARQUIVO_MENSAGENS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            MENSAGENS,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

MENSAGENS = carregar_mensagens()

mensagem_escolhida = None

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
# GERENCIAR MENSAGENS
# ==============================

async def mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not MENSAGENS:
        await update.message.reply_text(
            "📝 Nenhuma mensagem cadastrada."
        )
        return

    texto = "📝 Mensagens salvas:\n\n"

    for numero, mensagem in MENSAGENS.items():
        texto += f"{numero}️⃣ {mensagem[:60]}\n\n"

    await update.message.reply_text(texto)

async def adicionar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Use:\n/adicionar sua mensagem"
        )
        return

    numero = str(len(MENSAGENS) + 1)

    MENSAGENS[numero] = " ".join(context.args)

    salvar_mensagens()

    await update.message.reply_text(
        f"✅ Mensagem {numero} adicionada!"
    )

async def editar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Use:\n/editar número nova mensagem"
        )
        return

    numero = context.args[0]

    if numero not in MENSAGENS:
        await update.message.reply_text(
            "⚠️ Mensagem não encontrada."
        )
        return

    MENSAGENS[numero] = " ".join(context.args[1:])

    salvar_mensagens()

    await update.message.reply_text(
        "✅ Mensagem editada!"
    )

async def apagar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return

    numero = context.args[0]

    if numero in MENSAGENS:

        del MENSAGENS[numero]

        salvar_mensagens()

        await update.message.reply_text(
            "🗑️ Mensagem apagada!"
        )

async def usar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mensagem_escolhida

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return

    numero = context.args[0]

    if numero in MENSAGENS:

        mensagem_escolhida = MENSAGENS[numero]

        await update.message.reply_text(
            f"✅ Mensagem {numero} selecionada!"
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

    legenda = mensagem_escolhida or ""

    if mensagem.caption:

        if legenda:
            legenda += "\n\n"

        legenda += mensagem.caption

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
# ÁLBUM
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

    midias = []

    legenda = mensagem_escolhida or ""

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
# VIP
# ==============================

async def entrarnovip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🔥 ENTRAR NO VIP 🔥",
        reply_markup=botoes_vip()
    )

# ==============================
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand("start", "BOT ON ✅"),
        BotCommand("divulgar", "DIVULGAR 🔥"),
        BotCommand("d_album", "DIVULGAR ÁLBUM 🖼️"),
        BotCommand("mensagens", "VER MENSAGENS 📝"),
        BotCommand("adicionar", "➕ ADICIONAR"),
        BotCommand("editar", "✏️ EDITAR"),
        BotCommand("usar", "✅ USAR"),
        BotCommand("apagar", "🗑️ APAGAR"),
        BotCommand("entrarnovip", "🔥 VIP")
    ]

    await app.bot.set_my_commands(comandos)

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

app.add_handler(CommandHandler("mensagens", mensagens))
app.add_handler(CommandHandler("adicionar", adicionar_mensagem))
app.add_handler(CommandHandler("editar", editar_mensagem))
app.add_handler(CommandHandler("usar", usar_mensagem))
app.add_handler(CommandHandler("apagar", apagar_mensagem))

app.add_handler(CommandHandler("entrarnovip", entrarnovip))

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO,
        receber_album
    )
)

print("Bot iniciado ✅")

app.run_polling()