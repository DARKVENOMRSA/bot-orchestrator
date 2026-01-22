import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID") or "0")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
