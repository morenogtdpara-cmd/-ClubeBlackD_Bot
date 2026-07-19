import sqlite3
from config import DB_PATH

def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    c = conectar()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            conteudo TEXT,
            file_id TEXT,
            agendado_para TEXT,
            status TEXT DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            nome TEXT,
            mensagem TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            user_id INTEGER,
            detalhes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        );
    """)
    c.commit()
    c.close()

# --- Broadcasts ---
def salvar_broadcast(tipo, conteudo=None, file_id=None, agendado_para=None):
    c = conectar()
    c.execute("INSERT INTO broadcasts (tipo, conteudo, file_id, agendado_para) VALUES (?, ?, ?, ?)",
              (tipo, conteudo, file_id, agendado_para))
    c.commit()
    bid = c.lastrowid
    c.close()
    return bid

def listar_broadcasts_pendentes():
    c = conectar()
    rows = c.execute("SELECT * FROM broadcasts WHERE status='pendente' ORDER BY criado_em DESC").fetchall()
    c.close()
    return rows

def listar_broadcasts_agendados():
    c = conectar()
    rows = c.execute("SELECT * FROM broadcasts WHERE status='agendado' ORDER BY agendado_para ASC").fetchall()
    c.close()
    return rows

def listar_todos_broadcasts(limite=20):
    c = conectar()
    rows = c.execute("SELECT * FROM broadcasts ORDER BY criado_em DESC LIMIT ?", (limite,)).fetchall()
    c.close()
    return rows

def marcar_broadcast_enviado(bid):
    c = conectar()
    c.execute("UPDATE broadcasts SET status='enviado' WHERE id=?", (bid,))
    c.commit()
    c.close()

def cancelar_broadcast(bid):
    c = conectar()
    c.execute("UPDATE broadcasts SET status='cancelado' WHERE id=?", (bid,))
    c.commit()
    c.close()

# --- Feedbacks ---
def salvar_feedback(user_id, username, nome, mensagem):
    c = conectar()
    c.execute("INSERT INTO feedbacks (user_id, username, nome, mensagem) VALUES (?, ?, ?, ?)",
              (user_id, username, nome, mensagem))
    c.commit()
    c.close()

def listar_feedbacks(limite=30):
    c = conectar()
    rows = c.execute("SELECT * FROM feedbacks ORDER BY criado_em DESC LIMIT ?", (limite,)).fetchall()
    c.close()
    return rows

def contar_feedbacks():
    c = conectar()
    r = c.execute("SELECT COUNT(*) FROM feedbacks").fetchone()[0]
    c.close()
    return r

# --- Stats ---
def registrar_evento(evento, user_id=None, detalhes=None):
    c = conectar()
    c.execute("INSERT INTO stats (evento, user_id, detalhes) VALUES (?, ?, ?)",
              (evento, user_id, detalhes))
    c.commit()
    c.close()

def contar_eventos(evento):
    c = conectar()
    r = c.execute("SELECT COUNT(*) FROM stats WHERE evento=?", (evento,)).fetchone()[0]
    c.close()
    return r

def contar_usuarios_unicos():
    c = conectar()
    r = c.execute("SELECT COUNT(DISTINCT user_id) FROM stats WHERE user_id IS NOT NULL").fetchone()[0]
    c.close()
    return r

# --- Configurações ---
def get_config(chave, padrao=None):
    c = conectar()
    r = c.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,)).fetchone()
    c.close()
    return r[0] if r else padrao

def set_config(chave, valor):
    c = conectar()
    c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))
    c.commit()
    c.close()
    
    Show! Entendi a ansiedade haha. Vou jogar o código completão aqui pra tu. É um projeto mais parrudo, então preparei ele bem organizado. Bora lá que o código é grande mas tá tudo no jeito! 🚀





 

 

 📁  requirements.txt 

 





 

 





 

 

 📁  config.py 

 





 

 





 

 

 📁  database.py 

 





 

 





 

 Agora o arquivo principal:





 📁  main.py 

 



```python
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode



from config import BOTTOKEN, GRUPO ID, ADMIN_ID
from database import *





 ==================== ESTADOS ====================

 


 Dicionário para gerenciar estados dos usuários

 
estados = {}           # user_id -> estado
dadosestado = {}      # user id -> dict com dados temporários
bufferalbum = {}      # media group_id -> lista de mensagens
albumtimers = {}      # media group_id -> task





 ==================== TECLADOS ====================

 



def teclado_painel():
    return InlineKeyboardMarkup([
        InlineKeyboardButton("📢 Nova Divulgação", callback_data="broadcast_novo"),
        InlineKeyboardButton("📋 Ver Agendamentos", callback_data="agendamentos_listar"),
        [InlineKeyboardButton("💬 Ver Feedbacks", callbackdata="feedbacks ver"),
         InlineKeyboardButton("📊 Estatísticas", callbackdata="stats ver")],
        InlineKeyboardButton("⚙️ Configurações", callback_data="config_abrir"),
        InlineKeyboardButton("❌ Fechar Painel", callback_data="painel_fechar"),
    ])



def teclado_voltar():
    return InlineKeyboardMarkup([
        InlineKeyboardButton("🔙 Voltar ao Painel", callback_data="painel_abrir")
    ])



def tecladoconfirmar broadcast(bid):
    return InlineKeyboardMarkup([
        InlineKeyboardButton("✅ Enviar Agora", callback_data=f"broadcast_enviar_{bid}"),
        InlineKeyboardButton("⏰ Agendar", callback_data=f"broadcast_agendar_{bid}"),
        InlineKeyboardButton("❌ Cancelar", callback_data=f"broadcast_cancelar_{bid}"),
    ])



def teclado_config():
    return InlineKeyboardMarkup([
        InlineKeyboardButton("📝 Mensagem de Boas-vindas", callback_data="config_boasvindas"),
        InlineKeyboardButton("📢 Mensagem de Divulgação Padrão", callback_data="config_padrao"),
        InlineKeyboardButton("🔙 Voltar ao Painel", callback_data="painel_abrir"),
    ])





 ==================== VERIFICAÇÕES ====================

 



def ehadmin(user id: int) -> bool:
    return userid == ADMIN ID



async def verificar_admin(update: Update) -> bool:
    user = update.effective_user
    if not user or user.id != ADMIN_ID:
        if update.callback_query:
            await update.callbackquery.answer("🚫 Acesso restrito ao administrador.", show alert=True)
        else:
            await update.message.reply_text("🚫 Este comando é restrito ao administrador.")
        return False
    return True





 ==================== COMANDOS GERAIS ====================

 



async def cmdstart(update: Update, context: ContextTypes.DEFAULT TYPE):
    user = update.effective_user
    nome = user.first_name or "usuário"
    registrar_evento("start", user.id, nome)



    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👑 Olá, <b>{nome}</b>! Bem-vindo ao painel do <b>Bot de Divulgação</b>.\n\n"
            f"Use /painel para acessar o painel de controle.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                InlineKeyboardButton("🎛️ Abrir Painel", callback_data="painel_abrir")
            ])
        )
    else:
        await update.message.reply_text(
            f"👋 Olá, <b>{nome}</b>!\n\n"
            f"Envie /feedback para deixar sua opinião ou sugestão.\n"
            f"Use /help para ver todos os comandos.",
            parse_mode=ParseMode.HTML
        )



async def cmdhelp(update: Update, context: ContextTypes.DEFAULT TYPE):
    txt = (
        "📋 <b>Comandos Disponíveis</b>\n\n"
        "/start - Iniciar o bot\n"
        "/feedback - Enviar um feedback\n"
        "/help - Esta mensagem\n"
    )
    if update.effectiveuser.id == ADMIN ID:
        txt += "\n🔐 <b>Comandos Admin:</b>\n/painel - Painel de controle"
    await update.message.replytext(txt, parse mode=ParseMode.HTML)





 ==================== PAINEL ADMIN ====================

 



async def painelabrir(update: Update, context: ContextTypes.DEFAULT TYPE):
    if not await verificar_admin(update):
        return



    query = update.callback_query
    if query:
        await query.answer()
        await query.editmessage text(
            "🎛️ <b>Painel de Controle</b>\n\nSelecione uma opção:",
            parse_mode=ParseMode.HTML,
            replymarkup=teclado painel()
        )
    else:
        await update.message.reply_text(
            "🎛️ <b>Painel de Controle</b>\n\nSelecione uma opção:",
            parse_mode=ParseMode.HTML,
            replymarkup=teclado painel()
        )



async def cmdpainel(update: Update, context: ContextTypes.DEFAULT TYPE):
    if not await verificar_admin(update):
        return
    await update.message.reply_text(
        "🎛️ <b>Painel de Controle</b>\n\nSelecione uma opção:",
        parse_mode=ParseMode.HTML,
        replymarkup=teclado painel()
    )



async def painelfechar(update: Update, context: ContextTypes.DEFAULT TYPE):
    query = update.callback_query
    await query.answer()
    await query.editmessage text("✅ Painel fechado. Use /painel para abrir novamente.")





 ==================== BROADCAST / DIVULGAÇÃO ====================

 



async def broadcastiniciar(update: Update, context: ContextTypes.DEFAULT TYPE):
    if not await verificar_admin(update):
        return



    query = update.callback_query
    await query.answer()



    userid = update.effective user.id
    estadosuser_id = "aguardandoconteudo broadcast"
    dadosestado[user id] = {}



    await query.editmessage text(
        "📢 <b>Nova Divulgação</b>\n\n"
        "Envie o conteúdo que deseja divulgar no grupo.\n\n"
        "Pode ser:\n"
        "• Um texto\n"
        "• Uma foto (com legenda opcional)\n"
        "• Um vídeo (com legenda opcional)\n"
        "• Várias fotos/vídeos (álbum)\n\n"
        "<i>Envie o conteúdo agora...</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            InlineKeyboardButton("🔙 Cancelar", callback_data="painel_abrir")
        ])
    )



async def receberconteudo broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userid = update.effective user.id
    if estados.get(userid) != "aguardando conteudo_broadcast":
        return



    msg = update.message
    mediagroup id = msg.mediagroup id



    # Se faz parte de um álbum, aguardar todas as mídias
    if mediagroup id:
        if mediagroup id not in buffer_album:
            bufferalbum[media group_id] = []
        bufferalbum[media group_id].append(msg)



        # Cancela timer anterior se existir
        if mediagroup id in album_timers:
            albumtimers[media group_id].cancel()



        # Cria novo timer para processar o álbum
        async def processar_album(mgid):
            await asyncio.sleep(1.2)  # Aguarda outras mídias chegarem
            msgs = buffer_album.pop(mgid, [])
            album_timers.pop(mgid, None)
            if msgs:
                await finalizarcaptura broadcast(user_id, msgs, update, context)



        albumtimers[media groupid] = asyncio.create task(processaralbum(media group_id))
        return  # Não processa ainda, aguarda o timer



    # Conteúdo único (texto, foto ou vídeo)
    await finalizarcaptura broadcast(user_id, msg, update, context)



async def finalizarcaptura broadcast(user_id, mensagens, update, context):
    """Processa as mensagens capturadas e pergunta confirmação."""
    estadosuser_id = None
    dados = {"mensagens": [], "tipo": None}



    for msg in mensagens:
        if msg.photo:
            dados"mensagens".append({"tipo": "photo", "fileid": msg.photo[-1].file id, "caption": msg.caption})
        elif msg.video:
            dados"mensagens".append({"tipo": "video", "fileid": msg.video.file id, "caption": msg.caption})
        elif msg.text:
            dados"mensagens".append({"tipo": "text", "texto": msg.text})



    if not dados"mensagens":
        await update.message.reply_text("⚠️ Nenhum conteúdo válido detectado. Tente novamente.")
        return



    # Define tipo geral
    if len(dados"mensagens") > 1:
        dados"tipo" = "album"
    else:
        dados"tipo" = dados"mensagens""tipo"



    dadosestado[user id] = dados



    # Salva no banco
    import json
    bid = salvar_broadcast(
        tipo=dados"tipo",
        conteudo=json.dumps(dados"mensagens", ensure_ascii=False)
    )
    dados"bid" = bid



    # Preview
    tipo_nome = {"text": "📝 Texto", "photo": "🖼️ Foto", "video": "🎬 Vídeo", "album": "🖼️🎬 Álbum"}
    preview = f"📢 <b>Pré-visualização da Divulgação</b>\n\nTipo: {tipo_nome.get(dados'tipo', dados'tipo')}\nMídias: {len(dados'mensagens')}\n\nDeseja enviar agora ou agendar?"
    await update.message.replytext(preview, parse mode=ParseMode.HTML, replymarkup=teclado confirmar_broadcast(bid))



async def broadcastenviar(update: Update, context: ContextTypes.DEFAULT TYPE):
    if not await verificar_admin(update):
        return
    query = update.callback_query
    await query.answer()



    bid = int(query.data.split("_")-1)
    await enviarpara grupo(bid, context)
    marcarbroadcast enviado(bid)
    registrarevento("broadcast enviado", update.effective_user.id, f"bid={bid}")



    await query.editmessage text("✅ Divulgação enviada com sucesso ao grupo!", replymarkup=teclado voltar())



async def enviarpara grupo(bid, context):
    import json
    c = conectar()
    row = c.execute("SELECT tipo, conteudo FROM broadcasts WHERE id=?", (bid,)).fetchone()
    c.close()
    if not row:
        return



    tipo, conteudo_str = row
    mensagens = json.loads(conteudo_str)



    if tipo == "text":
        await context.bot.sendmessage(chat id=GRUPO_ID, text=mensagens0)
    elif tipo == "photo":
        m = mensagens0
        await context.bot.sendphoto(chat id=GRUPOID, photo=m["file id"], caption=m.get("caption") or "")
    elif tipo == "video":
        m = mensagens0
        await context.bot.sendvideo(chat id=GRUPOID, video=m["file id"], caption=m.get("caption") or "")
    elif tipo == "album":
        media_group = []
        for m in mensagens:
            if m"tipo" == "photo":
                mediagroup.append({"type": "photo", "media": m["file id"], "caption": m.get("caption") or ""})
            elif m"tipo" == "video":
                mediagroup.append({"type": "video", "media": m["file id"], "caption": m.get("caption") or ""})
        if media_group:
            await context.bot.sendmedia group(chatid=GRUPO ID, media=media_group)



async def broadcastagendar tela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await verificar_admin(update):
        return
    query = update.callback_query
    await query.answer()



    bid = int(query.data.split("_")-1)
    userid = update.effective user.id
    estadosuser_id = "aguardandodata agendamento"
    dadosestado[user id] = {"bid": bid}



    await query.editmessage text(
        "⏰ <b>Agendar Divulgação</b>\n\n"
        "Envie a data e hora no formato:\n"
        "<code>DD/MM/AAAA HH:MM</code>\n\n"
        "Exemplo: <code>25/12/2026 18:00</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            InlineKeyboardButton("🔙 Voltar", callback_data=f"broadcast_voltar_{bid}")
        ])
    )



async def receberdata agendamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userid = update.effective user.id
    if estados.get(userid) != "aguardando data_agendamento":
        return



    texto = update.message.text.strip()
    try:
        data_hora = datetime.strptime(texto, "%d/%m/%Y %H:%M