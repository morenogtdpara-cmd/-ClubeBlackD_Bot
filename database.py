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