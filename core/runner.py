import subprocess
import psutil
from core.registry import update_status

processes = {}

def start_bot(name, path):

    if name in processes:
        return False

    if path.endswith(".py"):
        proc = subprocess.Popen(["python", path])

    elif path.endswith(".js"):
        proc = subprocess.Popen(["node", path])

    else:
        return False

    processes[name] = proc
    update_status(name, "running", proc.pid)

    return True


def stop_bot(name):

    if name not in processes:
        return False

    proc = processes[name]

    try:
        psutil.Process(proc.pid).kill()
    except:
        pass

    update_status(name, "stopped", None)
    del processes[name]

    return True
