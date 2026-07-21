from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db
from feedback import FEEDBACK, abrir_feedback, receber_feedback
from handlers import (
    AGENDAMENTO_ALBUM,
    AGENDAMENTO_ESCOLHA,
    AGENDAMENTO_HORARIO,
    AGENDAMENTO_PUBLICACAO,
    ALBUM,
    abrir_agendamento,
    abrir_album,
    apagar_mensagem_avulsa,
    callbacks,
    cancelar_processo,
    escolher_agendamento_album,
    escolher_agendamento_unica,
    finalizar_agendamento_album,
    finalizar_album,
    manager,
    receber_agendamento_album,
    receber_agendamento_publicacao,
    receber_album,
    receber_divulgacao,
    receber_horario_agendamento,
    start,
)
from scheduler import iniciar_scheduler


def fallbacks_comuns():
    return [
        CallbackQueryHandler(
            cancelar_processo,
            pattern=r"^(cancelar_processo|cancelar_agendamento)$",
        ),
        CommandHandler("cancelar", cancelar_processo),
        CommandHandler("manager", manager),
        CommandHandler("start", start),
    ]


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    feedback_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                abrir_feedback,
                pattern=r"^feedbacks$",
            )
        ],
        states={
            FEEDBACK: [
                MessageHandler(
                    filters.ALL & ~filters.COMMAND,
                    receber_feedback,
                )
            ]
        },
        fallbacks=fallbacks_comuns(),
        allow_reentry=True,
    )

    album_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                abrir_album,
                pattern=r"^album_agora$",
            )
        ],
        states={
            ALBUM: [
                MessageHandler(
                    filters.ALL & ~filters.COMMAND,
                    receber_album,
                ),
                CallbackQueryHandler(
                    finalizar_album,
                    pattern=r"^finalizar_album$",
                ),
            ]
        },
        fallbacks=fallbacks_comuns(),
        allow_reentry=True,
    )

    agendamento_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                abrir_agendamento,
                pattern=r"^agendamento$",
            )
        ],
        states={
            AGENDAMENTO_ESCOLHA: [
                CallbackQueryHandler(
                    escolher_agendamento_unica,
                    pattern=r"^agendar_unica$",
                ),
                CallbackQueryHandler(
                    escolher_agendamento_album,
                    pattern=r"^agendar_album$",
                ),
            ],
            AGENDAMENTO_PUBLICACAO: [
                MessageHandler(
                    filters.ALL & ~filters.COMMAND,
                    receber_agendamento_publicacao,
                )
            ],
            AGENDAMENTO_ALBUM: [
                MessageHandler(
                    filters.ALL & ~filters.COMMAND,
                    receber_agendamento_album,
                ),
                CallbackQueryHandler(
                    finalizar_agendamento_album,
                    pattern=r"^finalizar_album_agendamento$",
                ),
            ],
            AGENDAMENTO_HORARIO: [
                MessageHandler(
                    filters.ALL & ~filters.COMMAND,
                    receber_horario_agendamento,
                )
            ],
        },
        fallbacks=fallbacks_comuns(),
        allow_reentry=True,
    )

    app.add_handler(feedback_handler)
    app.add_handler(album_handler)
    app.add_handler(agendamento_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manager", manager))
    app.add_handler(CommandHandler("cancelar", cancelar_processo))

    app.add_handler(CallbackQueryHandler(callbacks))

    app.add_handler(
        MessageHandler(
            filters.PHOTO
            | filters.VIDEO
            | (filters.TEXT & ~filters.COMMAND),
            receber_divulgacao,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            apagar_mensagem_avulsa,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.COMMAND,
            apagar_mensagem_avulsa,
        )
    )

    iniciar_scheduler(app)

    print("BOT ONLINE")
    app.run_polling()


if __name__ == "__main__":
    main()