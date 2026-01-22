from core.db import connect

def add_bot(name, file):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bots(name,file,status) VALUES(?,?,?)",
        (name, file, "stopped")
    )

    conn.commit()
    conn.close()


def list_bots():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT name,status FROM bots")
    data = cur.fetchall()

    conn.close()
    return data


def update_status(name, status, pid=None):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE bots SET status=?, pid=? WHERE name=?",
        (status, pid, name)
    )

    conn.commit()
    conn.close()
