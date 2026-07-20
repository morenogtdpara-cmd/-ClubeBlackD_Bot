from datetime import datetime

from telegram.ext import Application

from config import GROUP_ID, VIP_LINK
from fila import pegar_fila, remover_da_fila
from keyboards import vip_keyboard


async def verificar_fila(context):

    print("🔎 Verificando fila...")

    fila = pegar_fila()

    print("📋 Fila atual:", fila)

    agora = datetime.now().strftime("%H:%M")

    print("🕒 Hora do servidor:", agora)

    if not fila:
        return

    for indice, item in enumerate(fila):

        horario = item.get("horario")
        enviado = item.get("enviado", False)

        print(
            f"➡️ Item {item.get('id')} | Horário: {horario} | Enviado: {enviado}"
        )

        if horario == agora and not enviado:

            tipo = item.get("tipo")

            if tipo == "texto":

                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=item.get("conteudo"),
                    reply_markup=vip_keyboard(VIP_LINK)
                )

            remover_da_fila(indice)

            print(
                f"✅ Divulgação enviada e removida | ID {item.get('id')}"
            )

            break


def iniciar_scheduler(app: Application):

    if app.job_queue is None:
        print(
            "⚠️ JobQueue não disponível. Instale python-telegram-bot[job-queue]"
        )
        return

    app.job_queue.run_repeating(
        verificar_fila,
        interval=60,
        first=10
    )

    print(
        "⏰ Scheduler online"
    )