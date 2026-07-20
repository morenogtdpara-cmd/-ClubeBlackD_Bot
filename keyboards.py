from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def painel_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 DIVULGAR",
                callback_data="divulgar"
            ),
            InlineKeyboardButton(
                "🖼️ D/ÁLBUM",
                callback_data="album"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ FEEDBACKS",
                callback_data="feedbacks"
            ),
            InlineKeyboardButton(
                "⏰ AGENDAMENTO",
                callback_data="agendamento"
            )
        ],
        [
            InlineKeyboardButton(
                "⏰ FILA",
                callback_data="fila"
            )
        ]
    ])


def album_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 ENVIAR ÁLBUM",
                callback_data="album_agora"
            ),
            InlineKeyboardButton(
                "🔙 VOLTAR",
                callback_data="voltar"
            )
        ]
    ])


def vip_keyboard(link):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 ENTRAR NO VIP 🔥",
                url=link
            )
        ]
    ])


def fila_keyboard(itens, pagina=0):

    botoes = []

    inicio = pagina * 6
    fim = inicio + 6

    for indice, item in enumerate(
        itens[inicio:fim],
        start=inicio + 1
    ):
        botoes.append([
            InlineKeyboardButton(
                f"{indice} - {item}",
                callback_data=f"fila_item_{indice-1}"
            )
        ])

    navegacao = []

    if pagina > 0:
        navegacao.append(
            InlineKeyboardButton(
                "⬅️ ANTERIOR",
                callback_data=f"fila_pagina_{pagina-1}"
            )
        )

    if fim < len(itens):
        navegacao.append(
            InlineKeyboardButton(
                "➡️ PRÓXIMA",
                callback_data=f"fila_pagina_{pagina+1}"
            )
        )

    if navegacao:
        botoes.append(navegacao)

    return InlineKeyboardMarkup(botoes)


