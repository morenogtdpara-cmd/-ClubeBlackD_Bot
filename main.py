from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import asyncio

from config import BOT_TOKEN, ADMIN_ID
from database import init_db

GROUP_ID = -1004231485932

VIP_LINK = "https://t.me/ClubeBlackBot"

AGUARDANDO_DIVULGACAO = set()
AGUARDANDO_ALBUM = {}
ALBUNS_TEMP = {}
def botoes_vip():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔥 ENTRAR NO VIP 🔥",
                url=VIP_LINK
            )
        ]
    ])

def manager_keyboard():

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
                "📊 RELATÓRIO",
                callback_data="relatorio"
            )
        ],
        [
            InlineKeyboardButton(
                "⏰ FILA",
                callback_data="fila"
            )
        ]
    ])

def divulgar_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 ENVIAR AGORA",
                callback_data="divulgar_agora"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 AGENDAR DIVULGAÇÃO",
                callback_data="agendar_divulgacao"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 VOLTAR",
                callback_data="voltar_painel"
            )
        ]
    ])
def album_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 ENVIAR AGORA",
                callback_data="album_agora"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 AGENDAR ÁLBUM",
                callback_data="album_agendar"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 VOLTAR",
                callback_data="voltar_painel"
            )
        ]
    ])
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "Bot privado."
        )
        return

    await update.message.reply_text(
        "✅ Bot iniciado."
    )

async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚡️ PAINEL DE COMANDOS\n\nEscolha uma opção:",
        reply_markup=manager_keyboard()
    )

async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    if query.data == "divulgar":

        await query.message.reply_text(
            "📢 CENTRAL DE DIVULGAÇÃO",
            reply_markup=divulgar_keyboard()
        )

        return

    elif query.data == "divulgar_agora":

        AGUARDANDO_DIVULGACAO.add(
            query.from_user.id
        )

        await query.message.reply_text(
            "📤 Envie sua publicação."
        )

        return

    elif query.data == "agendar_divulgacao":

        await query.message.reply_text(
            "📅 Sistema de agendamento em construção."
        )

        return
    elif query.data == "album_agora":

        AGUARDANDO_ALBUM[query.from_user.id] = []

        await query.message.reply_text(
            "🖼️ Envie o álbum.\n\n"
            "📌 Máximo: 10 mídias."
        )

        return
    elif query.data == "fila":

        texto = (
            "⏰ FILA DE PUBLICAÇÕES\n\n"
            "📢 Divulgações aguardando: 0\n\n"
            "🖼️ Álbuns aguardando: 0\n\n"
            "📌 Total na fila: 0\n\n"
            "⚡ Sistema pronto."
        )


    elif query.data == "album":

        await query.message.reply_text(
            "🖼️ CENTRAL DE ÁLBUM\n\nEscolha uma opção:",
            reply_markup=album_keyboard()
        )

        return

    elif query.data == "feedbacks":

        texto = (
            "⭐ Feedbacks\n\n"
            "🚧 Em construção."
        )

    elif query.data == "relatorio":

        texto = (
            "📊 Relatório\n\n"
            "✅ Bot online."
        )

    elif query.data == "voltar_painel":

        await query.message.reply_text(
            "⚡️ PAINEL DE COMANDOS\n\nEscolha uma opção:",
            reply_markup=manager_keyboard()
        )

        return

    else:

        texto = "Opção inválida."

    await query.message.reply_text(
        texto
    )
async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    if update.effective_user.id not in AGUARDANDO_ALBUM:
        return

    if not update.message.media_group_id:
        return

    grupo_id = update.message.media_group_id

    if grupo_id not in ALBUNS_TEMP:
        ALBUNS_TEMP[grupo_id] = []

    if update.message.photo:

        ALBUNS_TEMP[grupo_id].append(
            {
                "tipo": "foto",
                "file_id": update.message.photo[-1].file_id,
                "legenda": update.message.caption
            }
        )

    elif update.message.video:

        ALBUNS_TEMP[grupo_id].append(
            {
                "tipo": "video",
                "file_id": update.message.video.file_id,
                "legenda": update.message.caption
            }
        )

    await asyncio.sleep(3)

    medias = ALBUNS_TEMP.get(grupo_id)

    if not medias:
        return

    await enviar_album(
        context,
        medias,
        medias[0].get("legenda")
    )

    del ALBUNS_TEMP[grupo_id]

    AGUARDANDO_ALBUM.pop(
        update.effective_user.id,
        None
    )

    await update.message.reply_text(
        "✅ Álbum enviado com sucesso."
    )
async def enviar_album(
    context,
    medias,
    legenda=None
):

    from telegram import InputMediaPhoto, InputMediaVideo

    grupo = []

    for i, media in enumerate(medias):

        if media["tipo"] == "foto":

            grupo.append(
                InputMediaPhoto(
                    media=media["file_id"],
                    caption=legenda if i == 0 else None
                )
            )

        elif media["tipo"] == "video":

            grupo.append(
                InputMediaVideo(
                    media=media["file_id"],
                    caption=legenda if i == 0 else None
                )
            )

    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=grupo
    )
async def receber_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    if update.effective_user.id not in AGUARDANDO_DIVULGACAO:
        return

    if update.message.photo:

        await context.bot.send_photo(
            chat_id=GROUP_ID,
            photo=update.message.photo[-1].file_id,
            caption=update.message.caption,
            reply_markup=botoes_vip()
        )

    elif update.message.video:

        await context.bot.send_video(
            chat_id=GROUP_ID,
            video=update.message.video.file_id,
            caption=update.message.caption,
            reply_markup=botoes_vip()
        )

    elif update.message.text:

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=update.message.text,
            reply_markup=botoes_vip()
        )

    else:

        await update.message.reply_text(
            "⚠️ Envie texto, foto ou vídeo."
        )

        return

    AGUARDANDO_DIVULGACAO.remove(
        update.effective_user.id
    )

    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )

def main():

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "manager",
            manager
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks
        )
    )

    app.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
                | filters.TEXT
            ),
            receber_divulgacao
        )
    )

    print("BOT ONLINE")

    app.run_polling()

if __name__ == "__main__":
    main()