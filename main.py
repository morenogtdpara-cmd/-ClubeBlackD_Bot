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

"""🚀 AS NOVIDADES CONTINUAM A TODO VAPOR! 🚀

Nossa comunidade segue trazendo atualizações e melhorias para quem gosta de acompanhar tudo de perto. Estamos sempre buscando oferecer uma experiência organizada, rápida e cheia de novidades para todos que participam.

🔥 Entre agora e veja tudo que está acontecendo!""",

"""💎 UM ESPAÇO PREPARADO PARA QUEM GOSTA DE NOVIDADES! 💎

Aqui você encontra uma comunidade em crescimento, com atualizações frequentes e novidades chegando constantemente. Cada detalhe é pensado para deixar sua experiência ainda melhor.

⚡ Venha conhecer e faça parte!""",

"""🔥 VOCÊ ESTÁ PERDENDO AS ÚLTIMAS NOVIDADES? 🔥

Não fique de fora enquanto novas atualizações estão sendo liberadas. Nossa comunidade está sempre ativa e trazendo conteúdos renovados para quem acompanha de perto.

🚀 Entre agora e confira!""",

"""🚨 ATENÇÃO PARA ESSA NOVIDADE! 🚨

Estamos trazendo melhorias e atualizações para deixar tudo mais completo. Quem participa acompanha de perto todas as novidades e fica sempre conectado com o que acontece por aqui.

🌟 Faça parte agora!""",

"""⚡ A MELHOR HORA PARA ENTRAR É AGORA! ⚡

Nossa comunidade está crescendo todos os dias e novas novidades estão chegando constantemente. Não espere mais para conhecer um espaço feito para quem gosta de estar atualizado.

🔥 Acesse e participe!""",

]"""👑 FAÇA PARTE DE ALGO QUE ESTÁ CRESCENDO! 👑

Cada vez mais pessoas estão chegando para acompanhar nossas atualizações e novidades. Junte-se a uma comunidade ativa e fique por dentro de tudo que está sendo preparado.

🚀 Entre agora!""",

"""💥 TEM SEMPRE UMA NOVIDADE ESPERANDO POR VOCÊ! 💥

Nossa equipe trabalha para manter tudo atualizado e trazer conteúdos novos regularmente. Se você gosta de acompanhar novidades, esse é o momento de participar.

⚡ Venha conferir!""",

"""🌟 NOVIDADES, ATUALIZAÇÕES E MUITO MAIS! 🌟

Nossa comunidade está preparada para quem gosta de acompanhar conteúdos renovados e estar sempre por dentro das novidades. Todos os dias buscamos trazer algo novo para nossos participantes.

🚀 Junte-se agora!""",

"""🚀 A COMUNIDADE QUE ESTÁ CHAMANDO ATENÇÃO! 🚀

Com novidades chegando todos os dias e uma comunidade cada vez maior, esse é o momento perfeito para entrar e acompanhar tudo desde o início.

👀 Descubra agora o que está disponível!""",

"""🔥 CHEGAMOS A UM NOVO NÍVEL! 🔥

Continuamos trazendo melhorias, atualizações e novidades para oferecer uma experiência cada vez mais completa. Quem participa acompanha tudo de perto e faz parte desse crescimento.

💎 Entre agora e venha conhecer!""",

"""🚨 TEM NOVIDADE CHEGANDO E VOCÊ NÃO PODE FICAR DE FORA! 🚨

Nossa comunidade está sempre recebendo atualizações e novos conteúdos para quem gosta de acompanhar tudo de perto. Trabalhamos constantemente para manter tudo organizado e atualizado.

🔥 Entre agora e descubra!""",

"""⚡ A ATUALIZAÇÃO QUE VOCÊ ESTAVA ESPERANDO CHEGOU! ⚡

Novidades estão sendo adicionadas e a comunidade continua crescendo todos os dias. Aqui você acompanha tudo de forma simples e rápida.

🚀 Faça parte agora!""",

"""🔥 NÃO SEJA O ÚLTIMO A DESCOBRIR! 🔥

Enquanto muitos ainda estão procurando onde acompanhar novidades, nossa comunidade já está trazendo atualizações constantes.

👀 Venha conferir agora!""",

"""💎 UM ESPAÇO CRIADO PARA QUEM BUSCA NOVIDADES! 💎

Nossa comunidade foi preparada para oferecer uma experiência completa, com organização, atualizações frequentes e novidades chegando sempre.

🌟 Entre hoje e conheça!""",

"""🚨 ATENÇÃO: TEM MUITA COISA NOVA POR AQUI! 🚨

Estamos sempre trazendo novidades e melhorias para deixar a comunidade cada vez mais completa.

🔥 Não fique de fora, participe agora!""",

"""🌟 SEMPRE TEM ALGO NOVO PARA DESCOBRIR! 🌟

Nossa comunidade está em constante movimento, com novidades chegando e atualizações sendo feitas regularmente. Um lugar para quem gosta de acompanhar tudo sem perder tempo.

⚡ Acesse agora e confira!""",

"""🚀 A COMUNIDADE ESTÁ CRESCENDO CADA VEZ MAIS! 🚀

Cada atualização traz algo novo e cada dia é uma nova oportunidade de descobrir novidades. Estamos sempre buscando melhorar e trazer uma experiência diferenciada.

💎 Venha fazer parte!"""

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