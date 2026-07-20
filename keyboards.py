from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def painel_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 DIVULGAR",
                callback_data="divulgar"
            ),
            InlineKeyboardButton(
                "🖼️ ÁLBUM",
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