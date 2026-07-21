from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import InputMediaPhoto, InputMediaVideo
from telegram.ext import Application

from config import GROUP_ID, VIP_LINK
from fila import pegar_fila, remover_da_fila
from keyboards import vip_keyboard
from database import adicionar_envio, adicionar_album


LEGENDA_FIXA_ALBUM = (
    "🔥 CONTEÚDO EXCLUSIVO\n\n"
    "Veja o conteúdo completo no VIP:\n"
    f"{VIP_LINK}"
)


async def verificar_fila(context):
    fila = pegar_fila()

    if not fila:
        return

    fuso = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso)
    indices_enviados = []

    for indice, item in enumerate(fila):
        if item.get("enviado", False):
            continue

        data = item.get("data")
        horario = item.get("horario")

        if not data or not horario:
            print("⚠️ Item sem data ou horário:", item)
            continue

        try:
            momento_programado = datetime.strptime(
                f"{data} {horario}",
                "%Y-%m-%d %H:%M",
            ).replace(tzinfo=fuso)
        except ValueError:
            print("⚠️ Data ou horário inválido:", item)
            continue

        if momento_programado > agora:
            continue

        tipo = item.get("tipo")
        conteudo = item.get("conteudo", "")
        arquivo = item.get("arquivo")

        try:
            if tipo == "texto":
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=conteudo,
                    reply_markup=vip_keyboard(VIP_LINK),
                )

            elif tipo == "foto":
                await context.bot.send_photo(
                    chat_id=GROUP_ID,
                    photo=arquivo,
                    caption=conteudo or None,
                    reply_markup=vip_keyboard(VIP_LINK),
                )

            elif tipo == "video":
                await context.bot.send_video(
                    chat_id=GROUP_ID,
                    video=arquivo,
                    caption=conteudo or None,
                    reply_markup=vip_keyboard(VIP_LINK),
                )

            elif tipo == "album":
                midias = item.get("midias", [])

                if not 2 <= len(midias) <= 10:
                    print("⚠️ Álbum inválido:", item)
                    continue

                lista_envio = []

                for indice_midia, midia in enumerate(midias):
                    legenda = LEGENDA_FIXA_ALBUM if indice_midia == 0 else None

                    if midia.get("tipo") == "foto":
                        lista_envio.append(
                            InputMediaPhoto(
                                media=midia.get("id"),
                                caption=legenda,
                            )
                        )

                    elif midia.get("tipo") == "video":
                        lista_envio.append(
                            InputMediaVideo(
                                media=midia.get("id"),
                                caption=legenda,
                            )
                        )

                if len(lista_envio) < 2:
                    print("⚠️ Álbum sem mídias válidas:", item)
                    continue

                await context.bot.send_media_group(
                    chat_id=GROUP_ID,
                    media=lista_envio,
                )

                adicionar_album(len(lista_envio))

            else:
                print("⚠️ Tipo inválido:", tipo)
                continue

        except Exception as erro:
            print("❌ Erro ao enviar publicação programada:", erro)
            continue

        adicionar_envio(1)
        indices_enviados.append(indice)

        print(f"✅ Publicação programada enviada: {item.get('id')}")

    for indice in reversed(indices_enviados):
        remover_da_fila(indice)


def iniciar_scheduler(app: Application):
    if app.job_queue is None:
        print(
            "⚠️ JobQueue não disponível. "
            "Instale python-telegram-bot[job-queue]"
        )
        return

    app.job_queue.run_repeating(
        verificar_fila,
        interval=30,
        first=5,
    )

    print("⏰ SCHEDULER ONLINE")