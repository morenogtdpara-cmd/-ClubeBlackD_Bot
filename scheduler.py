from telegram.ext import Application

from fila import pegar_fila


def iniciar_scheduler(app: Application):

    fila = pegar_fila()

    print(
        f"SCHEDULER ONLINE | Itens na fila: {len(fila)}"
    )