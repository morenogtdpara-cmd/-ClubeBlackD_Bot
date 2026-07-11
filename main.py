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
"""🚨 VOCÊ AINDA NÃO VIU TUDO! 🚨

Tem novidades chegando e muita coisa preparada para quem gosta de acompanhar conteúdos diferenciados.

🔥 Entre agora e descubra o que está esperando por você!""",

"""🔥 ACESSO LIBERADO! 🔥

Uma nova experiência está disponível. Estamos trazendo atualizações constantes para quem procura algo diferente e quer estar sempre por dentro das novidades.

🚀 Confira agora!""",

"""👀 CURIOSO PARA SABER O QUE TEM AQUI? 👀

Muita gente já está acompanhando as novidades. Não fique de fora, venha conferir e descubra por que esse espaço está crescendo cada vez mais.

💎 Acesse agora!""",

"""🚀 NOVIDADES CHEGANDO TODOS OS DIAS! 🚀

Um espaço atualizado, organizado e preparado para quem busca algo diferente.

🔥 Entre agora e acompanhe tudo de perto!""",

"""💎 NÃO PERCA ESSA OPORTUNIDADE! 💎

Estamos sempre trazendo novidades e melhorias para entregar uma experiência cada vez melhor para quem participa.

⚡ Venha conhecer!""",

"""⚡ VOCÊ ESTÁ A UM CLIQUE DE DESCOBRIR! ⚡

Tudo preparado para quem gosta de novidades e quer acompanhar conteúdos atualizados em um só lugar.

🚀 Confira agora!""",

"""👑 UM ESPAÇO PARA QUEM PROCURA ALGO A MAIS! 👑

Entre e conheça uma comunidade que está crescendo todos os dias com novidades e atualizações constantes.

🔥 Faça parte!""",

"""🔥 TEM MUITA COISA ACONTECENDO POR AQUI! 🔥

Não deixe para depois. Confira agora as novidades e veja o que está disponível.

👀 Entre agora!""",

"""🚨 NOVAS ATUALIZAÇÕES DISPONÍVEIS! 🚨

Estamos trazendo conteúdos renovados e deixando tudo ainda mais completo para quem acompanha.

💎 Confira!""",

"""🌟 A EXPERIÊNCIA QUE VOCÊ ESTAVA PROCURANDO! 🌟

Organização, novidades e atualizações em um só lugar.

🚀 Faça parte agora!"""
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