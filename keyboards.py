from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def painel_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 DIVULGAR",
                    callback_data="divulgar",
                ),
                InlineKeyboardButton(
                    "🖼️ ÁLBUM",
                    callback_data="album",
                ),
            ],
            [
                InlineKeyboardButton(
                    "⭐ FEEDBACKS",
                    callback_data="feedbacks",
                ),
                InlineKeyboardButton(
                    "⏰ AGENDAR",
                    callback_data="agendamento",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📋 PROGRAMADAS",
                    callback_data="fila",
                )
            ],
        ]
    )


def album_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📤 CRIAR NOVO ÁLBUM",
                    callback_data="album_agora",
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ VOLTAR AO PAINEL",
                    callback_data="voltar",
                )
            ],
        ]
    )


def vip_keyboard(link):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔥 ENTRAR NO VIP 🔥",
                    url=link,
                )
            ]
        ]
    )


def agendamento_tipo_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📄 PUBLICAÇÃO ÚNICA",
                    callback_data="agendar_unica",
                )
            ],
            [
                InlineKeyboardButton(
                    "🖼️ ÁLBUM",
                    callback_data="agendar_album",
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ VOLTAR AO PAINEL",
                    callback_data="cancelar_agendamento",
                )
            ],
        ]
    )


def finalizar_agendamento_album_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ FINALIZAR ÁLBUM",
                    callback_data="finalizar_album_agendamento",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ CANCELAR",
                    callback_data="cancelar_agendamento",
                )
            ],
        ]
    )


def cancelar_agendamento_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ CANCELAR",
                    callback_data="cancelar_agendamento",
                )
            ]
        ]
    )


def voltar_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "↩️ VOLTAR AO PAINEL",
                    callback_data="voltar",
                )
            ]
        ]
    )


def fila_keyboard(itens, pagina=0):
    botoes = []
    inicio = pagina * 6
    fim = inicio + 6

    nomes_tipos = {
        "texto": "TEXTO",
        "foto": "FOTO",
        "video": "VÍDEO",
        "album": "ÁLBUM",
    }

    for indice_real, item in enumerate(
        itens[inicio:fim],
        start=inicio,
    ):
        horario = item.get("horario", "--:--")
        tipo = nomes_tipos.get(item.get("tipo"), "PUBLICAÇÃO")

        if item.get("tipo") == "album":
            quantidade = len(item.get("midias", []))
            texto = f"⏰ {horario} • {tipo} ({quantidade})"
        else:
            texto = f"⏰ {horario} • {tipo}"

        botoes.append(
            [
                InlineKeyboardButton(
                    texto,
                    callback_data=f"fila_item_{indice_real}",
                )
            ]
        )

    navegacao = []

    if pagina > 0:
        navegacao.append(
            InlineKeyboardButton(
                "⬅️ ANTERIOR",
                callback_data=f"fila_pagina_{pagina - 1}",
            )
        )

    if fim < len(itens):
        navegacao.append(
            InlineKeyboardButton(
                "PRÓXIMA ➡️",
                callback_data=f"fila_pagina_{pagina + 1}",
            )
        )

    if navegacao:
        botoes.append(navegacao)

    botoes.append(
        [
            InlineKeyboardButton(
                "↩️ VOLTAR AO PAINEL",
                callback_data="voltar",
            )
        ]
    )

    return InlineKeyboardMarkup(botoes)


def fila_item_keyboard(indice):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑️ CANCELAR PUBLICAÇÃO",
                    callback_data=f"fila_remover_{indice}",
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ VOLTAR ÀS PROGRAMADAS",
                    callback_data="fila",
                )
            ],
        ]
    )
