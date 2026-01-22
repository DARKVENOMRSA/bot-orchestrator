import subprocess
import psutil
from core.db import connect

processes = {}

MAX_RAM = 300   # MB per bot
MAX_CPU = 60    # % per bot


def register_bot(name, path):
    con = connect()
    cur = con.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO bots VALUES(?,?,?,?,?)",
        (name, path, None, "stopped", "")
    )

    con.commit()
    con.close()


def list_bots():
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT name,status FROM bots")
    data = cur.fetchall()

    con.close()
    return data


def start_bot(name, path):

    if name in processes:
        return False, "Already running"

    if path.endswith(".py"):
        proc = subprocess.Popen(["python", path])

    elif path.endswith(".js"):
        proc = subprocess.Popen(["node", path])

    else:
        return False, "Unsupported file"

    processes[name] = proc

    con = connect()
    cur = con.cursor()

    cur.execute(
        "UPDATE bots SET pid=?, status=? WHERE name=?",
        (proc.pid, "running", name)
    )

    con.commit()
    con.close()

    return True, "Started"


def stop_bot(name):

    if name not in processes:
        return False, "Not running"

    proc = processes[name]

    try:
        psutil.Process(proc.pid).kill()
    except:
        pass

    del processes[name]

    con = connect()
    cur = con.cursor()

    cur.execute(
        "UPDATE bots SET pid=?, status=? WHERE name=?",
        (None, "stopped", name)
    )

    con.commit()
    con.close()

    return True, "Stopped"


# ===== AUTO RESTORE FUNCTION =====

def restore_bots():

    print("♻ Restoring previous bots...")

    con = connect()
    cur = con.cursor()

    cur.execute("SELECT name, path FROM bots WHERE status='running'")
    bots = cur.fetchall()

    con.close()

    for name, path in bots:
        try:
            ok, _ = start_bot(name, path)
            if ok:
                print(f"✅ Restored {name}")
        except:
            print(f"❌ Failed restore {name}")


# ===== WATCHDOG =====

def watchdog():

    for name, proc in list(processes.items()):

        try:
            p = psutil.Process(proc.pid)

            ram = p.memory_info().rss / 1024 / 1024
            cpu = p.cpu_percent(interval=1)

            if ram > MAX_RAM or cpu > MAX_CPU:

                p.kill()
                del processes[name]

                con = connect()
                cur = con.cursor()

                cur.execute(
                    "UPDATE bots SET status=?, last_error=? WHERE name=?",
                    ("killed", "Resource limit exceeded", name)
                )

                con.commit()
                con.close()

                print(f"⚠ {name} killed (resource limit)")

        except:
            pass
