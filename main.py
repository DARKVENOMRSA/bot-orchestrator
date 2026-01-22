from core.db import init_db
from services.control_bot import start_bot_panel

init_db()
print("System Ready")

start_bot_panel()
