from aiohttp import web, ClientSession
import os


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

        async with ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
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