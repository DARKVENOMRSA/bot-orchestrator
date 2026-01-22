import subprocess
import os

BOT_FOLDER = "bots"

running_processes = []

def list_bots():
    if not os.path.exists(BOT_FOLDER):
        os.mkdir(BOT_FOLDER)

    return [f for f in os.listdir(BOT_FOLDER) if f.endswith(".py")]

def start_bot_process(bot_name):
    path = os.path.join(BOT_FOLDER, bot_name)

    proc = subprocess.Popen(["python", path])
    running_processes.append(proc)
