import sqlite3
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