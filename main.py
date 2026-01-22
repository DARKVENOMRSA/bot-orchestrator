from fastapi import FastAPI, Request
import uvicorn
from telegram import Update
from services.control_bot import get_bot_app
from config import BOT_TOKEN, PORT, PUBLIC_DOMAIN

WEBHOOK_PATH = "/webhook"

app = FastAPI()
bot_app = get_bot_app()


@app.on_event("startup")
async def startup():

    await bot_app.initialize()

    webhook_url = f"https://{PUBLIC_DOMAIN}{WEBHOOK_PATH}"

    await bot_app.bot.set_webhook(webhook_url)

    print("✅ Webhook set:", webhook_url)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}


@app.get("/")
async def home():
    return {"status": "ONLINE"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
