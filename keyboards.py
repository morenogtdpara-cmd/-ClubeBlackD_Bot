def album_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 ENVIAR ÁLBUM",
                callback_data="album_agora"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ FINALIZAR ÁLBUM",
                callback_data="finalizar_album"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 VOLTAR",
                callback_data="voltar"
            )
        ]
    ])