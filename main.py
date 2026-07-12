import os
import random
import asyncio

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
    filters
)


BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1004231485932
OWNER_ID = 8880948641

VIP_LINK = "https://t.me/ClubeBlackBot"


MENSAGEM_EXTRA = """
🔥 ATUALIZAÇÃO DIÁRIA 🔥
💎 CONTEÚDO EXCLUSIVO
👑 ENTRE NO VIP 👑
"""


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


albuns = {}def botoes_vip():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥ENTRAR NO VIP 🔥",
                url=VIP_LINK
            )
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "BOT ON ✅\n\nUse /divulgar ou /d_album para enviar uma postagem."
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

    legenda = random.choice(FRASES) + "\n\n" + MENSAGEM_EXTRA

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


async def receber_album(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    mensagem = update.message

    if not mensagem.media_group_id:
        return

    if mensagem.media_group_id not in albuns:
        albuns[mensagem.media_group_id] = []

    albuns[mensagem.media_group_id].append(mensagem)

    await asyncio.sleep(2)


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
            "⚠️ Álbum não encontrado. Envie o álbum e aguarde."
        )
        return

    legenda = random.choice(FRASES) + "\n\n" + MENSAGEM_EXTRA

    for i, item in enumerate(albuns[grupo]):
        await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=item.chat.id,
            message_id=item.message_id,
            caption=legenda if i == 0 else None,
            reply_markup=botoes_vip() if i == 0 else None
        )

    del albuns[grupo]

    await update.message.reply_text(
        "✅ Álbum divulgado!"
    )async def configurar_menu(app):
    comandos = [
        BotCommand("start", "BOT ON ✅"),
        BotCommand("divulgar", "DIVULGAR 🔥"),
        BotCommand("d_album", "DIVULGAR ÁLBUM 🖼️")
    ]

    await app.bot.set_my_commands(comandos)


app = Application.builder().token(BOT_TOKEN).post_init(configurar_menu).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("divulgar", divulgar))
app.add_handler(CommandHandler("d_album", d_album))

app.add_handler(
    MessageHandler(
        filters.ALL,
        receber_album
    )
)


print("Bot iniciado")

app.run_polling()