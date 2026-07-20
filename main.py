from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from handlers import (
    start,
    manager,
    callbacks,
    receber_divulgacao,
    receber_album,
    finalizar_album
)

from config import BOT_TOKEN
from database import init_db
from scheduler import iniciar_scheduler
from feedback import abrir_feedback, receber_feedback

ALBUM = 1
FEEDBACK = 2

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


    # FEEDBACK (fica antes do callback geral)
    app.add_handler(
        CallbackQueryHandler(
            abrir_feedback,
            pattern="^feedbacks$"
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            callbacks,
            pattern="^(?!album_agora$|finalizar_album$).*"
        )
    )


    album_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                callbacks,
                pattern="^album_agora$"
            )
        ],
        states={
            ALBUM: [
                MessageHandler(
                    filters.PHOTO | filters.VIDEO,
                    receber_album
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                finalizar_album,
                pattern="^finalizar_album$"
            )
        ]
    )


    app.add_handler(
        album_handler
    )


    app.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.TEXT
            ),
            receber_divulgacao
        )
    )

    iniciar_scheduler(app)


    print("BOT ONLINE")


    app.run_polling()


if __name__ == "__main__":
    main()