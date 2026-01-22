import sqlite3
import os

os.makedirs("data", exist_ok=True)

DB = "data/manager.db"


def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bots(
        name TEXT PRIMARY KEY,
        path TEXT,
        pid INTEGER,
        status TEXT,
        last_error TEXT
    )
    """)

    con.commit()
    con.close()


def get_all_bots():
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT name, path, status FROM bots")
    data = cur.fetchall()

    con.close()
    return data
