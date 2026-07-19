from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from handlers import (
    start,
    manager,
    callbacks,
    receber_divulgacao
)
from config import BOT_TOKEN
from database import init_db
from handlers import (
    start,
    manager,
    callbacks
)
from scheduler import iniciar_scheduler


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


    iniciar_scheduler(app)


    print("BOT ONLINE")


    app.run_polling()


if __name__ == "__main__":
    main()