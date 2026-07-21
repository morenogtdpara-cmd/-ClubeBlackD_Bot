import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from config import DB_PATH


FUSO = ZoneInfo("America/Sao_Paulo")


def conectar():
    return sqlite3.connect(DB_PATH, timeout=30)


def init_db():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                username TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS relatorio_diario (
                data TEXT PRIMARY KEY,
                envios INTEGER DEFAULT 0,
                midias INTEGER DEFAULT 0,
                albuns INTEGER DEFAULT 0,
                agendados INTEGER DEFAULT 0
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS painel_admin (
                chat_id INTEGER PRIMARY KEY,
                message_id INTEGER NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mensagens_temporarias (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id)
            )
            """
        )


def salvar_usuario(user_id, nome, username):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO usuarios (id, nome, username)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nome = excluded.nome,
                username = excluded.username
            """,
            (user_id, nome, username),
        )


def data_hoje():
    return datetime.now(FUSO).strftime("%d/%m/%Y")


def criar_relatorio():
    with conectar() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO relatorio_diario
            (data, envios, midias, albuns, agendados)
            VALUES (?, 0, 0, 0, 0)
            """,
            (data_hoje(),),
        )


def pegar_relatorio():
    criar_relatorio()

    with conectar() as conn:
        resultado = conn.execute(
            """
            SELECT envios, midias, albuns, agendados
            FROM relatorio_diario
            WHERE data = ?
            """,
            (data_hoje(),),
        ).fetchone()

    return resultado or (0, 0, 0, 0)


def adicionar_envio(midias=1):
    criar_relatorio()

    with conectar() as conn:
        conn.execute(
            """
            UPDATE relatorio_diario
            SET envios = envios + 1,
                midias = midias + ?
            WHERE data = ?
            """,
            (midias, data_hoje()),
        )


def adicionar_album(midias):
    criar_relatorio()

    with conectar() as conn:
        conn.execute(
            """
            UPDATE relatorio_diario
            SET envios = envios + 1,
                albuns = albuns + 1,
                midias = midias + ?
            WHERE data = ?
            """,
            (midias, data_hoje()),
        )


def salvar_painel(chat_id, message_id):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO painel_admin (chat_id, message_id)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                message_id = excluded.message_id
            """,
            (chat_id, message_id),
        )


def pegar_painel(chat_id):
    with conectar() as conn:
        resultado = conn.execute(
            """
            SELECT message_id
            FROM painel_admin
            WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()

    return resultado[0] if resultado else None


def registrar_mensagem_temporaria(chat_id, message_id):
    with conectar() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO mensagens_temporarias
            (chat_id, message_id)
            VALUES (?, ?)
            """,
            (chat_id, message_id),
        )


def listar_mensagens_temporarias(chat_id):
    with conectar() as conn:
        resultados = conn.execute(
            """
            SELECT message_id
            FROM mensagens_temporarias
            WHERE chat_id = ?
            ORDER BY message_id
            """,
            (chat_id,),
        ).fetchall()

    return [resultado[0] for resultado in resultados]


def remover_mensagem_temporaria(chat_id, message_id):
    with conectar() as conn:
        conn.execute(
            """
            DELETE FROM mensagens_temporarias
            WHERE chat_id = ? AND message_id = ?
            """,
            (chat_id, message_id),
        )


def limpar_mensagens_temporarias_db(chat_id):
    with conectar() as conn:
        conn.execute(
            """
            DELETE FROM mensagens_temporarias
            WHERE chat_id = ?
            """,
            (chat_id,),
        )
