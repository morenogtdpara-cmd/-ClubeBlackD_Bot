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
    finalizar_album,
    receber_agendamento_publicacao,
    receber_horario_agendamento,
    cancelar_agendamento,
    ALBUM,
    AGENDAMENTO_PUBLICACAO,
    AGENDAMENTO_HORARIO
)

from config import BOT_TOKEN
from database import init_db
from scheduler import iniciar_scheduler
from feedback import abrir_feedback, receber_feedback


FEEDBACK = 2


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

    feedback_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                abrir_feedback,
                pattern=r"^feedbacks$"
            )
        ],
        states={
            FEEDBACK: [
                MessageHandler(
                    filters.PHOTO,
                    receber_feedback
                )
            ]
        },
        fallbacks=[],
        allow_reentry=True
    )

    app.add_handler(
        feedback_handler
    )

    album_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                callbacks,
                pattern=r"^album_agora$"
            )
        ],
        states={
            ALBUM: [
                MessageHandler(
                    filters.PHOTO | filters.VIDEO,
                    receber_album
                ),
                CallbackQueryHandler(
                    finalizar_album,
                    pattern=r"^finalizar_album$"
                )
            ]
        },
        fallbacks=[],
        allow_reentry=True
    )

    app.add_handler(
        album_handler
    )

    agendamento_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                callbacks,
                pattern=r"^agendamento$"
            )
        ],
        states={
            AGENDAMENTO_PUBLICACAO: [
                MessageHandler(
                    (
                        filters.PHOTO
                        | filters.VIDEO
                        | (
                            filters.TEXT
                            & ~filters.COMMAND
                        )
                    ),
                    receber_agendamento_publicacao
                )
            ],
            AGENDAMENTO_HORARIO: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    receber_horario_agendamento
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                cancelar_agendamento,
                pattern=r"^cancelar_agendamento$"
            )
        ],
        allow_reentry=True
    )

    app.add_handler(
        agendamento_handler
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks,
            pattern=(
                r"^(?!(?:"
                r"album_agora|"
                r"finalizar_album|"
                r"agendamento|"
                r"cancelar_agendamento"
                r")$).*"
            )
        )
    )

    app.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.VIDEO
                | (
                    filters.TEXT
                    & ~filters.COMMAND
                )
            ),
            receber_divulgacao
        )
    )

    iniciar_scheduler(
        app
    )

    print(
        "BOT ONLINE"
    )

    app.run_polling()


if __name__ == "__main__":
    main()