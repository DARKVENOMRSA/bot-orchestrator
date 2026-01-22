import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "5725238764"))
PORT = int(os.getenv("PORT", "8080"))

PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")
