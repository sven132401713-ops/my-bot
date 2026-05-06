from aiohttp import web
import os
import requests


VK_CONFIRMATION = os.getenv("VK_CONFIRMATION")
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle(request):
    data = await request.json()

    event_type = data.get("type")

    if event_type == "confirmation":
        return web.Response(text=VK_CONFIRMATION or "")

    if event_type == "message_new":
        message = data.get("object", {}).get("message", {})
        text_from_vk = message.get("text", "")
        user_id = message.get("from_id", "")

        text = (
            "🆕 Новое сообщение из VK:\n\n"
            f"{text_from_vk}\n\n"
            f"VK user id: {user_id}"
        )

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": ADMIN_ID,
                "text": text
            },
            timeout=10
        )

        return web.Response(text="ok")

    return web.Response(text="ok")


def setup_vk_app():
    app = web.Application()
    app.router.add_post("/", handle)
    app.router.add_get("/", lambda request: web.Response(text="VK bot is running"))
    return app