from aiohttp import web, ClientSession, FormData
import os
import random
import json
from bot.database import save_order, save_client
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


async def send_vk_photo(user_id, image_path):
    async with ClientSession() as session:
        async with session.post(
            "https://api.vk.com/method/photos.getMessagesUploadServer",
            data={
                "access_token": VK_TOKEN,
                "peer_id": user_id,
                "group_id": 190030234,
                "v": "5.199"
            }
        ) as response:
            upload_data = await response.json()

        if "response" not in upload_data:
            await send_telegram_message(
                "❌ Ошибка VK при получении upload_url:\n"
                f"{upload_data}"
            )
            return

        upload_url = upload_data["response"]["upload_url"]

        form = FormData()
        with open(image_path, "rb") as photo_file:
            form.add_field(
                "photo",
                photo_file,
                filename=os.path.basename(image_path),
                content_type="image/png"
            )

            async with session.post(upload_url, data=form) as response:
                if response.content_type != "application/json":
                    await send_telegram_message(
                        "❌ VK не принял фото. Попробуйте нажать прайс ещё раз."
                    )
                    return

                uploaded = await response.json()

        async with session.post(
            "https://api.vk.com/method/photos.saveMessagesPhoto",
            data={
                "access_token": VK_TOKEN,
                "photo": uploaded["photo"],
                "server": uploaded["server"],
                "hash": uploaded["hash"],
                "v": "5.199"
            }
        ) as response:
            saved_data = await response.json()

        if "response" not in saved_data:
            await send_telegram_message(
                "❌ Ошибка VK при сохранении фото:\n"
                f"{saved_data}"
            )
            return

        photo = saved_data["response"][0]
        attachment = f"photo{photo['owner_id']}_{photo['id']}"

        await session.post(
            "https://api.vk.com/method/messages.send",
            data={
                "access_token": VK_TOKEN,
                "user_id": user_id,
                "message": "📋 Прайс лист",
                "attachment": attachment,
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
        text_lower = text_from_vk.lower()
        user_id = message.get("from_id", "")
        save_client(
            platform="VK",
            client_id=str(user_id),
            client_name="VK клиент",
            username=f"vk_{user_id}"
        )        

        greetings = [
            "/start",
            "начать",
            "старт",
            "привет",
            "здравствуйте",
            "добрый день",
            "добрый вечер",
            "доброе утро"
        ]

        if text_lower in greetings or len(text_from_vk) < 15:
            await send_vk_message(user_id, "Здравствуйте! Выберите нужный раздел:")
            return web.Response(text="ok")

        if text_from_vk == "📋 Прайс лист":
            base_dir = os.path.abspath(os.path.join(os.getcwd(), "images"))

            await send_vk_photo(user_id, os.path.join(base_dir, "price1.png"))
            await send_vk_photo(user_id, os.path.join(base_dir, "price2.png"))
            await send_vk_photo(user_id, os.path.join(base_dir, "price3.png"))

            await send_vk_message(user_id, "Для заказа нажмите «🛒 Сделать заказ».")
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
        save_order(
            source="VK",
            order_text=text_from_vk,
            client_username=f"vk_{user_id}",
            client_id=str(user_id),
            client_name="VK клиент"
        )                
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