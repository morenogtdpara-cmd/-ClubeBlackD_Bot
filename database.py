import sqlite3
from config import DB_PATH


def conectar():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = conectar()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sistema (
            id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()