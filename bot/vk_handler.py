from aiohttp import web, ClientSession
import os
import random
import json

VK_CONFIRMATION = os.getenv("VK_CONFIRMATION")
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
VK_TOKEN = os.getenv("VK_TOKEN")


DELIVERY_TEXT = (
    "🚚 Доставка:\n\n"
    "Доставка осуществляется до двери по Самаре и Новокуйбышевску.\n\n"
    "📅 Дни доставки:\n"
    "— вторник\n"
    "— пятница\n\n"
    "💰 Условия:\n"
    "Минимальный заказ от 1000 рублей.\n\n"
    "От 1000 до 2500 — доставка 150 рублей.\n"
    "От 2500 — доставка бесплатная."
)

ORDER_TEXT = (
    "🛒 Напишите заказ одним сообщением.\n\n"
    "Укажите, пожалуйста:\n"
    "— что хотите заказать и количество\n"
    "— имя\n"
    "— телефон\n"
    "— адрес доставки\n\n"
    "Например:\n"
    "Сметана 2 кг, творог 1 кг, манты с горбушей 1 кг, Андрей, "
    "+79991839372, Самара, Дыбенко 20.\n\n"
    "Если потребуется уточнение, менеджер свяжется с вами."
)

CONTACT_TEXT = (
    "📞 Связь с менеджером:\n\n"
    "Телефон: +79874416997\n"
    "Telegram: @ferma_163\n\n"
    "🕒 Время работы:\n"
    "Ежедневно с 09:00 до 20:00"
)


def get_vk_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [{"action": {"type": "text", "label": "📋 Прайс лист"}, "color": "primary"}],
            [{"action": {"type": "text", "label": "🛒 Сделать заказ"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "🚚 Информация по доставке"}, "color": "secondary"}],
            [{"action": {"type": "text", "label": "☎️ Связаться с менеджером"}, "color": "secondary"}],
        ]
    }


async def send_vk_message(user_id, text):
    async with ClientSession() as session:
        await session.post(
            "https://api.vk.com/method/messages.send",
            data={
                "access_token": VK_TOKEN,
                "user_id": user_id,
                "message": text,
                "random_id": random.randint(1, 999999999),
                "keyboard": json.dumps(get_vk_keyboard(), ensure_ascii=False),
                "v": "5.199"
            }
        )


async def send_telegram_message(text):
    async with ClientSession() as session:
        await session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": ADMIN_ID,
                "text": text
            }
        )


async def handle(request):
    data = await request.json()
    event_type = data.get("type")

    if event_type == "confirmation":
        return web.Response(text=VK_CONFIRMATION or "")

    if event_type == "message_new":
        message = data.get("object", {}).get("message", {})
        text_from_vk = message.get("text", "").strip()
        user_id = message.get("from_id", "")

        if text_from_vk.lower() in ["/start", "начать", "старт", "привет"]:
            await send_vk_message(user_id, "Здравствуйте! Выберите нужный раздел:")
            return web.Response(text="ok")

        if text_from_vk == "📋 Прайс лист":
            await send_vk_message(
                user_id,
                "📋 Прайс лист пока доступен в Telegram-боте.\n\n"
                "Напишите заказ здесь одним сообщением, если уже знаете что нужно."
            )
            return web.Response(text="ok")

        if text_from_vk == "🛒 Сделать заказ":
            await send_vk_message(user_id, ORDER_TEXT)
            return web.Response(text="ok")

        if text_from_vk == "🚚 Информация по доставке":
            await send_vk_message(user_id, DELIVERY_TEXT)
            return web.Response(text="ok")

        if text_from_vk == "☎️ Связаться с менеджером":
            await send_vk_message(user_id, CONTACT_TEXT)
            return web.Response(text="ok")

        text = (
            "🆕 Новый заказ из VK:\n\n"
            f"{text_from_vk}\n\n"
            f"VK user id: {user_id}"
        )

        await send_telegram_message(text)

        await send_vk_message(
            user_id,
            "✅ Заказ принят!\n\n"
            "Мы получили вашу заявку.\n"
            "Свяжемся с вами в ближайшее время.\n\n"
            "Спасибо 🙌"
        )

        return web.Response(text="ok")

    return web.Response(text="ok")


def setup_vk_app():
    app = web.Application()
    app.router.add_post("/", handle)
    return app