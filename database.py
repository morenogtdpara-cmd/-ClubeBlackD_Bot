import sqlite3
from datetime import datetime

from config import DB_PATH


def conectar():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            username TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relatorio_diario (
            data TEXT PRIMARY KEY,
            envios INTEGER DEFAULT 0,
            midias INTEGER DEFAULT 0,
            albuns INTEGER DEFAULT 0,
            agendados INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def salvar_usuario(user_id, nome, username):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios
        (id, nome, username)
        VALUES (?, ?, ?)
    """, (
        user_id,
        nome,
        username
    ))

    conn.commit()
    conn.close()


def data_hoje():
    return datetime.now().strftime("%d/%m/%Y")


def criar_relatorio():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO relatorio_diario
        (data, envios, midias, albuns, agendados)
        VALUES (?, 0, 0, 0, 0)
    """, (
        data_hoje(),
    ))

    conn.commit()
    conn.close()


def pegar_relatorio():
    criar_relatorio()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT envios, midias, albuns, agendados
        FROM relatorio_diario
        WHERE data = ?
    """, (
        data_hoje(),
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado


def adicionar_envio(midias=1):
    criar_relatorio()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE relatorio_diario
        SET envios = envios + 1,
            midias = midias + ?
        WHERE data = ?
    """, (
        midias,
        data_hoje(),
    ))

    conn.commit()
    conn.close()


def adicionar_album(midias):
    criar_relatorio()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE relatorio_diario
        SET albuns = albuns + 1,
            midias = midias + ?
        WHERE data = ?
    """, (
        midias,
        data_hoje(),
    ))

    conn.commit()
    conn.close()


def adicionar_album(midias):
    criar_relatorio()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE relatorio_diario
        SET albuns = albuns + 1,
            midias = midias + ?
        WHERE data = ?
    """, (
        midias,
        data_hoje(),
    ))

    conn.commit()
    conn.close()