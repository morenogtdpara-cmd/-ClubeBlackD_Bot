from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def painel_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 𝐃𝐈𝐕𝐔𝐋𝐆𝐀𝐑",
                callback_data="divulgar"
            ),
            InlineKeyboardButton(
                "🖼️ 𝐀́𝐋𝐁𝐔𝐌",
                callback_data="album"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊𝐒",
                callback_data="feedbacks"
            ),
            InlineKeyboardButton(
                "⏰ 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎",
                callback_data="agendamento"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎𝐒",
                callback_data="fila"
            )
        ]
    ])


def album_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 𝐂𝐑𝐈𝐀𝐑 𝐍𝐎𝐕𝐎 𝐀́𝐋𝐁𝐔𝐌",
                callback_data="album_agora"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ 𝐕𝐎𝐋𝐓𝐀𝐑 𝐀𝐎 𝐏𝐀𝐈𝐍𝐄𝐋",
                callback_data="voltar"
            )
        ]
    ])


def vip_keyboard(link):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 𝐄𝐍𝐓𝐑𝐀𝐑 𝐍𝐎 𝐕𝐈𝐏 🔥",
                url=link
            )
        ]
    ])


def cancelar_agendamento_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❌ 𝐂𝐀𝐍𝐂𝐄𝐋𝐀𝐑 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎",
                callback_data="cancelar_agendamento"
            )
        ]
    ])


def voltar_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "↩️ 𝐕𝐎𝐋𝐓𝐀𝐑 𝐀𝐎 𝐏𝐀𝐈𝐍𝐄𝐋",
                callback_data="voltar"
            )
        ]
    ])


def fila_keyboard(
    itens,
    pagina=0
):

    botoes = []

    inicio = pagina * 6
    fim = inicio + 6

    nomes_tipos = {
        "texto": "TEXTO",
        "foto": "FOTO",
        "video": "VÍDEO"
    }

    for indice_real, item in enumerate(
        itens[inicio:fim],
        start=inicio
    ):

        horario = item.get(
            "horario",
            "--:--"
        )

        tipo = nomes_tipos.get(
            item.get("tipo"),
            "PUBLICAÇÃO"
        )

        botoes.append([
            InlineKeyboardButton(
                f"⏰ {horario} • {tipo}",
                callback_data=f"fila_item_{indice_real}"
            )
        ])

    navegacao = []

    if pagina > 0:

        navegacao.append(
            InlineKeyboardButton(
                "⬅️ 𝐀𝐍𝐓𝐄𝐑𝐈𝐎𝐑",
                callback_data=f"fila_pagina_{pagina - 1}"
            )
        )

    if fim < len(itens):

        navegacao.append(
            InlineKeyboardButton(
                "𝐏𝐑Ó𝐗𝐈𝐌𝐀 ➡️",
                callback_data=f"fila_pagina_{pagina + 1}"
            )
        )

    if navegacao:
        botoes.append(navegacao)

    botoes.append([
        InlineKeyboardButton(
            "↩️ 𝐕𝐎𝐋𝐓𝐀𝐑 𝐀𝐎 𝐏𝐀𝐈𝐍𝐄𝐋",
            callback_data="voltar"
        )
    ])

    return InlineKeyboardMarkup(
        botoes
    )


def fila_item_keyboard(
    indice
):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🗑️ 𝐂𝐀𝐍𝐂𝐄𝐋𝐀𝐑 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎",
                callback_data=f"fila_remover_{indice}"
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ 𝐕𝐎𝐋𝐓𝐀𝐑 𝐀𝐎𝐒 𝐀𝐆𝐄𝐍𝐃𝐀𝐌𝐄𝐍𝐓𝐎𝐒",
                callback_data="fila"
            )
        ]
    ])