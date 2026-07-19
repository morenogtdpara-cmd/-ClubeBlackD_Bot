from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_ID
from database import init_db

GROUP_ID = -1004231485932

VIP_LINK = "https://t.me/ClubeBlackBot"

AGUARDANDO_DIVULGACAO = set()

AGUARDANDO_ALBUM = set()

ALBUNS_TEMP = {}

def botoes_vip():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔥 ENTRAR NO VIP 🔥",
                    url=VIP_LINK
                )
            ]
        ]
    )

def manager_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 DIVULGAR",
                    callback_data="divulgar"
                ),
                InlineKeyboardButton(
                    "🖼️ ÁLBUM",
                    callback_data="album"
                )
            ]
        ]
    )

def divulgar_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📤 ENVIAR AGORA",
                    callback_data="divulgar_agora"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 VOLTAR",
                    callback_data="voltar"
                )
            ]
        ]
    )

def album_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📤 ENVIAR ÁLBUM",
                    callback_data="album_agora"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 VOLTAR",
                    callback_data="voltar"
                )
            ]
        ]
    )

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "✅ Bot online."
    )

async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "⚡ PAINEL",
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
            "📢 DIVULGAÇÃO",
            reply_markup=divulgar_keyboard()
        )

        return

    if query.data == "divulgar_agora":

        AGUARDANDO_DIVULGACAO.add(
            query.from_user.id
        )

        await query.message.reply_text(
            "📤 Envie a mídia."
        )

        return

    if query.data == "album":

        await query.message.reply_text(
            "🖼️ ÁLBUM",
            reply_markup=album_keyboard()
        )

        return

    if query.data == "album_agora":

        AGUARDANDO_ALBUM.add(
            query.from_user.id
        )

        await query.message.reply_text(
            "🖼️ Envie as mídias juntas.\n\n"
            "📌 Máximo: 10 mídias."
        )

        return

    if query.data == "voltar":

        await query.message.reply_text(
            "⚡ PAINEL",
            reply_markup=manager_keyboard()
        )

        return

async def receber_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in AGUARDANDO_ALBUM:
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
                "file_id": update.message.photo[-1].file_id
            }
        )

    elif update.message.video:

        ALBUNS_TEMP[grupo_id].append(
            {
                "tipo": "video",
                "file_id": update.message.video.file_id
            }
        )

    # espera novas mídias chegarem

    for job in context.job_queue.jobs():

        if job.name == f"album_{grupo_id}":

            job.schedule_removal()

    context.job_queue.run_once(
        fechar_album,
        2,
        data={
            "grupo_id": grupo_id,
            "user_id": user_id
        },
        name=f"album_{grupo_id}"
    )

async def fechar_album(
    context: ContextTypes.DEFAULT_TYPE
):

    grupo_id = context.job.data["grupo_id"]

    user_id = context.job.data["user_id"]

    medias = ALBUNS_TEMP.get(
        grupo_id,
        []
    )

    if medias:

        await enviar_album(
            context,
            medias
        )

    ALBUNS_TEMP.pop(
        grupo_id,
        None
    )

    AGUARDANDO_ALBUM.discard(
        user_id
    )

async def enviar_album(
    context,
    medias
):

    lista = []

    for media in medias[:10]:

        if media["tipo"] == "foto":

            lista.append(
                InputMediaPhoto(
                    media=media["file_id"]
                )
            )

        elif media["tipo"] == "video":

            lista.append(
                InputMediaVideo(
                    media=media["file_id"]
                )
            )

    if lista:

        await context.bot.send_media_group(
            chat_id=GROUP_ID,
            media=lista
        )

async def receber_divulgacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    # se estiver enviando álbum, ignora divulgação normal

    if user_id in AGUARDANDO_ALBUM:
        return

    if user_id not in AGUARDANDO_DIVULGACAO:
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

        return

    AGUARDANDO_DIVULGACAO.discard(
        user_id
    )

    await update.message.reply_text(
        "✅ Divulgação enviada com sucesso."
    )

def main():

    init_db()

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

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

    # ÁLBUM PRIMEIRO

    app.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
            ),
            receber_album
        ),
        group=0
    )

    # DIVULGAÇÃO NORMAL

    app.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
                | filters.TEXT
            ),
            receber_divulgacao
        ),
        group=1
    )

    print(
        "BOT ONLINE"
    )

    app.run_polling()

if __name__ == "__main__":

    main()