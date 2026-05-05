from aiohttp import web
import os
import json

VK_CONFIRMATION = os.getenv("VK_CONFIRMATION")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


async def handle(request):
    data = await request.json()

    if data["type"] == "confirmation":
        return web.Response(text=VK_CONFIRMATION)

    if data["type"] == "message_new":
        message = data["object"]["message"]["text"]
        user_id = data["object"]["message"]["from_id"]

        text = (
            "🆕 Новый заказ из VK:\n\n"
            f"{message}\n\n"
            f"VK user id: {user_id}"
        )

        # отправка в Telegram
        import requests
        bot_token = os.getenv("BOT_TOKEN")

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={
                "chat_id": ADMIN_ID,
                "text": text
            }
        )

        return web.Response(text="ok")

    return web.Response(text="ok")


def setup_vk_app():
    app = web.Application()
    app.router.add_post("/", handle)
    return app