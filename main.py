# ==============================
# DIVULGAR
# ==============================

async def divulgar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return


    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Responda uma foto ou vídeo usando /divulgar."
        )
        return


    mensagem = update.message.reply_to_message


    legenda = ""


    if mensagem_escolhida:

        legenda = mensagem_escolhida


    if mensagem.caption:

        if legenda:

            legenda += "\n\n"


        legenda += mensagem.caption


    await context.bot.copy_message(
        chat_id=GROUP_ID,
        from_chat_id=mensagem.chat.id,
        message_id=mensagem.message_id,
        caption=legenda if legenda else None,
        reply_markup=botoes_vip()
    )


    await update.message.reply_text(
        "✅ Divulgação enviada!"
    )



# ==============================
# RECEBER ÁLBUM
# ==============================

async def receber_album(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return


    mensagem = update.message


    if not mensagem.media_group_id:
        return


    grupo = mensagem.media_group_id


    if grupo not in albuns:

        albuns[grupo] = []


    albuns[grupo].append(mensagem)


    await asyncio.sleep(3)



# ==============================
# DIVULGAR ÁLBUM
# ==============================

async def d_album(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return


    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Responda o álbum usando /d_album."
        )
        return


    grupo = update.message.reply_to_message.media_group_id


    if not grupo or grupo not in albuns:

        await update.message.reply_text(
            "⚠️ Álbum não encontrado."
        )
        return


    midias = []


    legenda = ""


    if mensagem_escolhida:

        legenda = mensagem_escolhida



    for i, item in enumerate(albuns[grupo]):


        if item.photo:

            midias.append(
                InputMediaPhoto(
                    media=item.photo[-1].file_id,
                    caption=legenda if i == 0 and legenda else None
                )
            )


        elif item.video:

            midias.append(
                InputMediaVideo(
                    media=item.video.file_id,
                    caption=legenda if i == 0 and legenda else None
                )
            )


    await context.bot.send_media_group(
        chat_id=GROUP_ID,
        media=midias
    )


    del albuns[grupo]


    await update.message.reply_text(
        "✅ Álbum divulgado!"
    )



# ==============================
# ENTRAR NO VIP
# ==============================

async def entrarnovip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return


    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🔥 ENTRAR NO VIP 🔥",
        reply_markup=botoes_vip()
    )



# ==============================
# MENU
# ==============================

async def configurar_menu(app):

    comandos = [

        BotCommand("start", "BOT ON ✅"),

        BotCommand("divulgar", "DIVULGAR 🔥"),

        BotCommand("d_album", "DIVULGAR ÁLBUM 🖼️"),

        BotCommand("mensagens", "VER MENSAGENS 📝"),

        BotCommand("adicionar", "➕ ADICIONAR MENSAGEM"),

        BotCommand("editar", "✏️ EDITAR MENSAGEM"),

        BotCommand("usar", "✅ USAR MENSAGEM"),

        BotCommand("apagar", "🗑️ APAGAR MENSAGEM"),

        BotCommand("entrarnovip", "🔥 ENTRAR NO VIP 🔥")
    ]


    await app.bot.set_my_commands(comandos)



# ==============================
# CRIAR BOT
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

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("divulgar", divulgar))

app.add_handler(CommandHandler("d_album", d_album))

app.add_handler(CommandHandler("mensagens", mensagens))

app.add_handler(CommandHandler("adicionar", adicionar_mensagem))

app.add_handler(CommandHandler("editar", editar_mensagem))

app.add_handler(CommandHandler("usar", usar_mensagem))

app.add_handler(CommandHandler("apagar", apagar_mensagem))

app.add_handler(CommandHandler("entrarnovip", entrarnovip))



# ==============================
# RECEBER MÍDIAS
# ==============================

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO,
        receber_album
    )
)



print("Bot iniciado ✅")


app.run_polling()