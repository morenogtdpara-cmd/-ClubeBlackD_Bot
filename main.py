import os
import asyncio
import json

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
BOT_TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -1004231485932

OWNER_ID = 8880948641

VIP_LINK = "https://t.me/ClubeBlackBot"


# ==============================
# 🖤 BLACK SYSTEM - DADOS REAIS
# ==============================

ARQUIVO_SISTEMA = "black_system.json"


def carregar_sistema():

    if not Path(ARQUIVO_SISTEMA).exists():

        dados = {

            "data": "",

            "envios_hoje": 0,

            "midias_hoje": 0,

            "ultimo_envio": None,

            "ultimo_tipo": None,

            "ultimo_status": None,

            "feedbacks": 0,

            "albuns": 0,

            "divulgacoes": 0

        }

        salvar_sistema(dados)

        return dados


    with open(
        ARQUIVO_SISTEMA,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)



def salvar_sistema(dados):

    with open(
        ARQUIVO_SISTEMA,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



STATUS_SISTEMA = carregar_sistema()



def atualizar_dia():

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    data_atual = agora.strftime(
        "%d/%m/%Y"
    )


    if STATUS_SISTEMA["data"] != data_atual:

        STATUS_SISTEMA["data"] = data_atual

        STATUS_SISTEMA["envios_hoje"] = 0

        STATUS_SISTEMA["midias_hoje"] = 0

        salvar_sistema(
            STATUS_SISTEMA
        )



# ==============================
# REGISTROS DO SISTEMA
# ==============================

def atualizar_ultimo_envio(tipo, quantidade=1):

    STATUS_SISTEMA["envios_hoje"] += 1

    STATUS_SISTEMA["midias_hoje"] += quantidade

    STATUS_SISTEMA["ultimo_envio"] = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).strftime("%H:%M")

    STATUS_SISTEMA["ultimo_tipo"] = tipo

    STATUS_SISTEMA["ultimo_status"] = "Sucesso"

    salvar_sistema(
        STATUS_SISTEMA
    )


def registrar_divulgacao():

    atualizar_dia()

    STATUS_SISTEMA["divulgacoes"] += 1

    atualizar_ultimo_envio(
        "Publicação",
        1
    )


def registrar_album(quantidade):

    atualizar_dia()

    STATUS_SISTEMA["albuns"] += 1

    atualizar_ultimo_envio(
        "Álbum",
        quantidade
    )


def registrar_feedback():

    atualizar_dia()

    STATUS_SISTEMA["feedbacks"] += 1

    atualizar_ultimo_envio(
        "Feedback",
        1
    )

# ==============================
# LEGENDA FIXA
# ==============================

LEGENDA_FIXA = """
🔥 CONTEÚDO EXCLUSIVO LIBERADO 🔥

🚀 Acesse nosso canal oficial:
@ClubeBlackBot
"""


albuns = {}
aguardando_album = set()
albuns_processados = set()

modo_album = set()
modo_album_agendar = set()

album_agendar_temp = {}
# ==============================
# FEEDBACK - ESTADO
# ==============================

AGUARDANDO_FEEDBACK = 1

# ==============================
# AGENDAMENTOS
# ==============================

ARQUIVO_AGENDAMENTOS = "agendamentos.json"


def carregar_agendamentos():

    if not Path(
        ARQUIVO_AGENDAMENTOS
    ).exists():

        return []

    with open(
        ARQUIVO_AGENDAMENTOS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def salvar_agendamentos(lista):

    with open(
        ARQUIVO_AGENDAMENTOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            lista,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


agendamentos = carregar_agendamentos()


# ==============================
# BOTÃO VIP
# ==============================

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


# ==============================
# START
# ==============================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return


    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        "👑 Bem-vindo de volta, Chefe! 🥷🏾\n\n"

        "⚡ Sistema Ativo ⚡\n\n"

        "━━━━━━━━━━━\n\n"

        "📋 HOJE\n\n"

        f"👑 Envios: {STATUS_SISTEMA['envios_hoje']}/𝟐𝟎\n"

        f"📱 Mídias: {STATUS_SISTEMA['midias_hoje']}\n"

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "📊 ESTATÍSTICAS TOTAIS\n\n"

        f"📤 Divulgações: {STATUS_SISTEMA['divulgacoes']}\n"

        f"📚 Álbuns: {STATUS_SISTEMA['albuns']}\n"

        f"📨 Feedbacks: {STATUS_SISTEMA['feedbacks']}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Controle total\n"

        "⚡ Sistema protegido ⚡"

    )


# ==============================
# STATUS REAL
# ==============================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    atualizar_dia()

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    tempo = agora - INICIO_BOT

    horas = tempo.seconds // 3600

    minutos = (tempo.seconds % 3600) // 60

    proximo = "--:--"

    if agendamentos:

        horarios = sorted(

            [

                item["horario"]

                for item in agendamentos

            ]

        )

        proximo = horarios[0]

    ultimo = (

        STATUS_SISTEMA["ultimo_envio"]

        or "--:--"

    )

    await update.message.reply_text(

        "🖤 BLACK SYSTEM\n\n"

        "👑 Bem-vindo de volta, Chefe! 🥷🏾\n\n"

        f"⚡ Sistema Ativo há: {horas}h {minutos}m\n\n"

        "━━━━━━━━━━━\n\n"

        "📋 HOJE\n\n"

        f"👑 Envios: {STATUS_SISTEMA['envios_hoje']}/∞\n"

        f"📱 Mídias: {STATUS_SISTEMA['midias_hoje']}\n"

        f"⏰ Agendados: {len(agendamentos)}\n\n"

        "━━━━━━━━━━━\n\n"

        "⚡ PRÓXIMA DIVULGAÇÃO\n\n"

        f"🕙 {proximo}\n"

        "📢 Publicação\n\n"

        "━━━━━━━━━━━\n\n"

        "📌 ÚLTIMO ENVIO\n\n"

        f"🕘 {ultimo}\n"

        f"✅ {STATUS_SISTEMA['ultimo_status'] or '--'}\n\n"

        "━━━━━━━━━━━\n\n"

        "🥷🏾 Controle total\n"

        "⚡ Sistema protegido ⚡"

    )

# ==============================
# INICIAR FEEDBACK
# ==============================

async def feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    await update.message.reply_text(
        "📸 Envie a foto do feedback."
    )

    return AGUARDANDO_FEEDBACK
# ==============================
# RECEBER FEEDBACK
# ==============================

async def receber_feedback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:
        return

    foto = update.message.photo[-1].file_id

    LEGENDA_FEEDBACK = """
⭐ FEEDBACK REAL ⭐

🔥 Mais um cliente satisfeito com o Clube Black VIP.

💎 Conteúdo exclusivo.
⚡ Acesso rápido.
🖤 Experiência premium.

🚀 Entre para o VIP agora!
"""

    await context.bot.send_photo(

        chat_id=GROUP_ID,

        photo=foto,

        caption=LEGENDA_FEEDBACK,

        reply_markup=botoes_vip()

    )
    registrar_feedback()
    await update.message.reply_text(
        "✅ Feedback enviado com sucesso!"
    )

    return ConversationHandler.END
# ==============================
# RECEBER HORÁRIO ÁLBUM
# ==============================

async def receber_horario_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    usuario = update.effective_user.id

    if usuario not in album_agendar_temp:

        return

    horario = update.message.text.strip()

    try:

        datetime.strptime(
            horario,
            "%H:%M"
        )

    except:

        await update.message.reply_text(
            "⚠️ Horário inválido.\n\nExemplo: 14:00"
        )

        return


    grupo = album_agendar_temp[usuario]


    await update.message.reply_text(

        f"✅ Horário recebido: {horario}\n\n"

        "Próximo passo: salvar o álbum."

    )


    del album_agendar_temp[usuario]

# ==============================
# DIVULGAR ÁLBUM COMPLETO
# ==============================

async def divulgar_album_completo(
    context: ContextTypes.DEFAULT_TYPE
):

    grupo = context.job.data

    if grupo not in albuns:

        return

    midias = []

    legenda_usuario = albuns[grupo].get(
        "legenda",
        ""
    )

    if legenda_usuario:

        legenda_final = (

            legenda_usuario.strip()

            + "\n\n"

            + LEGENDA_FIXA.strip()

        )

    else:

        legenda_final = LEGENDA_FIXA.strip()

    for item in albuns[grupo]["mensagens"]:

        if item.photo:

            midias.append(

                InputMediaPhoto(

                    media=item.photo[-1].file_id,

                    caption=legenda_final
                    if len(midias) == 0
                    else None

                )

            )

        elif item.video:

            midias.append(

                InputMediaVideo(

                    media=item.video.file_id,

                    caption=legenda_final
                    if len(midias) == 0
                    else None

                )

            )

    if midias:

        await context.bot.send_media_group(

            chat_id=GROUP_ID,

            media=midias

        )

        registrar_album(
            len(midias)
        )

    del albuns[grupo]

# ==============================
# DIVULGAR
# ==============================

async def divulgar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        return

    mensagem = update.message.reply_to_message

    await context.bot.copy_message(

        chat_id=GROUP_ID,

        from_chat_id=mensagem.chat.id,

        message_id=mensagem.message_id,

        reply_markup=botoes_vip()

    )

    registrar_divulgacao()


# ==============================
# DIVULGAR ÁLBUM MANUAL
# ==============================

async def d_album(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        return

    grupo = update.message.reply_to_message.media_group_id

    if not grupo or grupo not in albuns:

        await update.message.reply_text(

            "⚠️ Álbum não encontrado."

        )

        return

    midias = []

    legenda_usuario = albuns[grupo].get(

        "legenda",

        ""

    )

    if legenda_usuario:

        legenda_final = (

            legenda_usuario.strip()

            + "\n\n"

            + LEGENDA_FIXA.strip()

        )

    else:

        legenda_final = LEGENDA_FIXA.strip()


    for item in albuns[grupo]["mensagens"]:

        if item.photo:

            midias.append(

                InputMediaPhoto(

                    media=item.photo[-1].file_id,

                    caption=legenda_final

                    if len(midias) == 0

                    else None

                )

            )


        elif item.video:

            midias.append(

                InputMediaVideo(

                    media=item.video.file_id,

                    caption=legenda_final

                    if len(midias) == 0

                    else None

                )

            )


    if midias:

        await context.bot.send_media_group(

            chat_id=GROUP_ID,

            media=midias

        )


    registrar_album(
    len(midias)
)


    del albuns[grupo]


    await update.message.reply_text(

        "✅ Álbum divulgado!"

    )


# ==============================
# AGENDAR PUBLICAÇÃO
# ==============================

async def agendar_publicacao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    if not update.message.reply_to_message:

        await update.message.reply_text(

            "⚠️ Responda a publicação e use /agendar HH:MM"

        )

        return

    if not context.args:

        await update.message.reply_text(

            "⚠️ Exemplo: /agendar 08:00"

        )

        return


    horario = context.args[0]


    try:

        datetime.strptime(

            horario,

            "%H:%M"

        )

    except:

        await update.message.reply_text(

            "⚠️ Horário inválido."

        )

        return


        mensagem = update.message.reply_to_message


    if mensagem.media_group_id:

        grupo = mensagem.media_group_id


        if grupo not in albuns:

            await update.message.reply_text(

                "⚠️ Álbum não encontrado."

            )

            return


        midias_album = []


        for item in albuns[grupo]["mensagens"]:

            if item.photo:

                midias_album.append({

                    "tipo": "foto",

                    "file_id": item.photo[-1].file_id

                })


            elif item.video:

                midias_album.append({

                    "tipo": "video",

                    "file_id": item.video.file_id

                })


        agendamentos.append({

            "horario": horario,

            "tipo": "album",

            "chat_id": GROUP_ID,

            "midias": midias_album,

            "legenda": albuns[grupo].get(

                "legenda",

                ""

            )

        })


        salvar_agendamentos(

            agendamentos

        )


        await update.message.reply_text(

            f"✅ Álbum agendado com sucesso!\n\n"

            f"📅 Horário: {horario}\n"

            f"🖼️ Tipo: Álbum"

        )


        return


    agendamentos.append({

        "horario": horario,

        "tipo": "publicacao",

        "chat_id": mensagem.chat.id,

        "message_id": mensagem.message_id

    })


    salvar_agendamentos(

        agendamentos

    )


    await update.message.reply_text(

        f"✅ Agendado com sucesso!\n\n"

        f"📅 Horário: {horario}\n"

        f"📢 Tipo: Publicação"

    )


# ==============================
# VERIFICAR AGENDAMENTOS
# ==============================

async def verificar_agendamentos(
    context: ContextTypes.DEFAULT_TYPE
):

    print("VERIFICANDO AGENDAMENTOS")


    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).strftime("%H:%M")


    for item in agendamentos.copy():

        if item["horario"] != agora:

            continue


        try:

            if item.get("tipo") == "album":

                midias = []


                legenda_usuario = item.get(
                    "legenda",
                    ""
                )


                if legenda_usuario:

                    legenda_final = (

                        legenda_usuario.strip()

                        + "\n\n"

                        + LEGENDA_FIXA.strip()

                    )

                else:

                    legenda_final = LEGENDA_FIXA.strip()


                for item_midia in item["midias"]:

                    if item_midia["tipo"] == "foto":

                        midias.append(

                            InputMediaPhoto(

                                media=item_midia["file_id"],

                                caption=legenda_final

                                if len(midias) == 0

                                else None

                            )

                        )


                    elif item_midia["tipo"] == "video":

                        midias.append(

                            InputMediaVideo(

                                media=item_midia["file_id"],

                                caption=legenda_final

                                if len(midias) == 0

                                else None

                            )

                        )


                if midias:

                    await context.bot.send_media_group(

                        chat_id=GROUP_ID,

                        media=midias

                    )


                registrar_album(
                    len(midias)
                )


                print("ÁLBUM ENVIADO ✅")


            else:

                await context.bot.copy_message(

                    chat_id=GROUP_ID,

                    from_chat_id=item["chat_id"],

                    message_id=item["message_id"],

                    reply_markup=botoes_vip()

                )


                registrar_divulgacao()


                print("PUBLICAÇÃO ENVIADA ✅")


            await context.bot.send_message(

                chat_id=OWNER_ID,

                text=(

                    "✅ Publicação enviada com sucesso!\n\n"

                    f"📅 Horário: {agora}\n"

                    f"📢 Tipo: {item.get('tipo', 'publicacao')}"

                )

            )


            agendamentos.remove(item)


            salvar_agendamentos(
                agendamentos
            )


        except Exception as e:

            print(
                "ERRO AO ENVIAR AGENDAMENTO:",
                e
            )


# ==============================
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

    BotCommand(
        "start",
        "BLACK SYSTEM 👑"
    ),

    BotCommand(
        "manager",
        "⚙️ BLACK COMMAND"
    ),

    BotCommand(
        "divulgar",
        "DIVULGAR 🔥"
    ),

    BotCommand(
        "d_album",
        "DIVULGAR ÁLBUM 🖼️"
    ),

    BotCommand(
        "agendar",
        "AGENDAR DIVULGAÇÃO ⏰"
    ),

    BotCommand(
        "feedback",
        "ADICIONAR FEEDBACK 📸"
    )

]


    await app.bot.set_my_commands(
        comandos
    )


# ==============================
# VIP
# ==============================

async def entrarnovip(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:

        return

    await context.bot.send_message(

        chat_id=GROUP_ID,

        text="",

        reply_markup=botoes_vip()

    )

# ==============================
# ⚙️ BLACK COMMAND
# ==============================

async def manager(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != OWNER_ID:
        return


    teclado = InlineKeyboardMarkup(

    [

        [

            InlineKeyboardButton(
                "📢 Divulgação",
                callback_data="command_divulgacao"
            )

        ],

        [

            InlineKeyboardButton(
                "📚 Álbuns",
                callback_data="command_album"
            )

        ],

        [

            InlineKeyboardButton(
                "⏰ Agendamentos",
                callback_data="command_agendamentos"
            )

        ],

        [

            InlineKeyboardButton(
                "📸 Feedbacks",
                callback_data="command_feedback"
            )

        ],

        [

            InlineKeyboardButton(
                "📊 Status",
                callback_data="command_status"
            )

        ],

        [

            InlineKeyboardButton(
                "🔥 VIP",
                callback_data="command_vip"
            )

        ]

    ]

)


    await update.message.reply_text(

        "⚙️ BLACK COMMAND\n\n"

        "👑 Controle de operações\n\n"

        "Escolha uma opção:",

        reply_markup=teclado

    )
# ==============================
# ⚙️ BLACK COMMAND - NAVEGAÇÃO
# ==============================

async def black_command_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    if query.data == "command_album":

        teclado = InlineKeyboardMarkup(

            [

                [

                    InlineKeyboardButton(
                        "📤 Enviar Agora",
                        callback_data="album_enviar"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "⏰ Agendar",
                        callback_data="album_agendar"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "🔙 Voltar",
                        callback_data="command_voltar"
                    )

                ]

            ]

        )


        await query.edit_message_text(

            "📚 DIVULGAÇÃO ÁLBUM\n\n"
            "Escolha uma opção:",

            reply_markup=teclado

        )


    elif query.data == "album_enviar":

        modo_album.add(

            update.effective_user.id

        )


        await query.edit_message_text(

            "📚 ÁLBUM\n\n"
            "Envie ou encaminhe o álbum que deseja divulgar."

        )


    elif query.data == "album_agendar":

        modo_album_agendar.add(

            update.effective_user.id

        )


        await query.edit_message_text(

            "⏰ AGENDAR ÁLBUM\n\n"
            "Envie ou encaminhe o álbum.\n\n"
            "Depois vou solicitar o horário."

        )


    elif query.data == "command_voltar":

        teclado = InlineKeyboardMarkup(

            [

                [

                    InlineKeyboardButton(
                        "📢 Divulgação",
                        callback_data="command_divulgacao"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "📚 Álbuns",
                        callback_data="command_album"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "⏰ Agendamentos",
                        callback_data="command_agendamentos"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "📸 Feedbacks",
                        callback_data="command_feedback"
                    )

                ],

                [

                    InlineKeyboardButton(
                        "📊 Status",
                        callback_data="command_status"
                    )

                ]

            ]

        )


        await query.edit_message_text(

            "⚙️ BLACK COMMAND\n\n"
            "Escolha uma opção:",

            reply_markup=teclado

        )
# ==============================
# BOT
# ==============================

app = (

    Application

    .builder()

    .token(BOT_TOKEN)

    .post_init(configurar_menu)

    .build()

)


# ==============================
# COMANDOS
# ==============================

app.add_handler(

    CommandHandler(
        "manager",
        manager
    )

)


app.add_handler(

    CommandHandler(
        "start",
        start
    )

)


app.add_handler(

    CommandHandler(
        "divulgar",
        divulgar
    )

)


app.add_handler(

    CommandHandler(
        "d_album",
        d_album
    )

)


app.add_handler(

    CommandHandler(
        "entrarnovip",
        entrarnovip
    )

)


app.add_handler(

    CommandHandler(
        "agendar",
        agendar_publicacao
    )

)


# ==============================
# FEEDBACK
# ==============================

app.add_handler(

    ConversationHandler(

        entry_points=[

            CommandHandler(
                "feedback",
                feedback
            )

        ],

        states={

            AGUARDANDO_FEEDBACK: [

                MessageHandler(
                    filters.PHOTO,
                    receber_feedback
                )

            ]

        },

        fallbacks=[]

    )

)


# ==============================
# ÁLBUM
# ==============================

app.add_handler(

    MessageHandler(

        filters.PHOTO | filters.VIDEO,

        receber_album

    )

)
app.add_handler(

    MessageHandler(

        filters.TEXT & ~filters.COMMAND,

        receber_horario_album

    )

)

# ==============================
# BOTÕES
# ==============================

app.add_handler(

    CallbackQueryHandler(

        black_command_menu

    )

)


# ==============================
# AGENDAMENTOS
# ==============================

app.job_queue.run_repeating(

    verificar_agendamentos,

    interval=30,

    first=10

)


print("Bot iniciado ✅")


app.run_polling()