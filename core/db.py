import sqlite3
import os

os.makedirs("data", exist_ok=True)

DB_FILE = "data/system.db"

def connect():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        file TEXT,
        status TEXT,
        pid INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
