import os
import random
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1004231485932
OWNER_ID = 8880948641

FRASES = [
    "🔥 O que era bom agora ficou ainda mais intenso. Confira agora.",
    "👀 Uma novidade acabou de chegar. Você vai querer ver.",
    "🌑 Algo especial está esperando por você.",
    "🚀 Atualização liberada. Aproveite essa novidade.",
    "👑 Conteúdo exclusivo disponível agora."
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "BOT ON ✅\n\nUse /divulgar para enviar uma postagem."
    )


async def divulgar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ Responda uma foto ou vídeo usando /divulgar."
        )
        return

    mensagem = update.message.reply_to_message
    legenda = random.choice(FRASES)

    botoes = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👑 BLACK VIP 👑",
                url="https://t.me/ClubeBlackBot"
            ),
            InlineKeyboardButton(
                "🛠️ SUPORTE 🛠️",
                url="https://t.me/KNOXX_VIP"
            )
        ]
    ])

    await context.bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=mensagem.chat.id,
        message_id=mensagem.message_id,
        caption=legenda,
        reply_markup=botoes
    )

    await update.message.reply_text(
        "✅ Divulgação enviada!"
    )


async def configurar_menu(app):
    comandos = [
        BotCommand("start", "BOT ON ✅"),
        BotCommand("divulgar", "DIVULGAR 🔥")
    ]

    await app.bot.set_my_commands(comandos)


app = Application.builder().token(BOT_TOKEN).post_init(configurar_menu).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("divulgar", divulgar))

print("Bot iniciado")

app.run_polling()