import psutil

def get_stats():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    running = len(psutil.pids())

    return cpu, ram, running
