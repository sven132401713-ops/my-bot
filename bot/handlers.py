from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiohttp import ClientSession
from bot.database import save_order
import os

router = Router()

ADMIN_ID = 5876599297


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Прайс лист")],
        [KeyboardButton(text="🛒 Сделать заказ")],
        [KeyboardButton(text="🚚 Информация по доставке")],
        [KeyboardButton(text="☎️ Связаться с менеджером")],
    ],
    resize_keyboard=True
)


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Здравствуйте! Выберите нужный раздел:",
        reply_markup=main_keyboard
    )


@router.message(F.text == "📋 Прайс лист")
async def price_handler(message: Message):
    await message.answer("📋 Отправляю прайс лист:")

    base_dir = os.path.abspath(os.path.join(os.getcwd(), "images"))

    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price1.png")))
    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price2.png")))
    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price3.png")))

    await message.answer(
        "Для заказа нажмите «🛒 Сделать заказ».",
        reply_markup=main_keyboard
    )


@router.message(F.text == "🚚 Информация по доставке")
async def delivery_handler(message: Message):
    await message.answer(
        "🚚 Доставка:\n\n"
        "Доставка осуществляется до двери по Самаре и Новокуйбышевску.\n\n"
        "📅 Дни доставки:\n"
        "— вторник\n"
        "— пятница\n\n"
        "💰 Условия:\n"
        "Минимальный заказ от 1000 рублей.\n\n"
        "От 1000 до 2500 — доставка 150 рублей.\n"
        "От 2500 — доставка бесплатная.",
        reply_markup=main_keyboard
    )


@router.message(F.text == "☎️ Связаться с менеджером")
async def contact_manager(message: Message):
    await message.answer(
        "📞 Связь с менеджером:\n\n"
        "Телефон: +79874416997\n"
        "Telegram: @ferma_163\n\n"
        "🕒 Время работы:\n"
        "Ежедневно с 9:00 до 20:00",
        reply_markup=main_keyboard
    )


@router.message(F.text == "🛒 Сделать заказ")
async def order_instruction(message: Message):
    await message.answer(
        "🛒 Напишите заказ одним сообщением.\n\n"
        "Укажите, пожалуйста:\n"
        "— что хотите заказать и количество\n"
        "— имя\n"
        "— телефон\n"
        "— адрес доставки\n\n"
        "Например:\n"
        "Сметана 2 кг, творог 1 кг, манты с горбушей 1 кг, Андрей, +79991839372, Самара, Дыбенко 20.\n\n"
        "Если потребуется уточнение, менеджер свяжется с вами.",
        reply_markup=main_keyboard
    )
@router.message(Command("vkreply"))
async def vk_reply_handler(message: Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Эта команда доступна только администратору.")
        return

    if not command.args:
        await message.answer(
            "Использование:\n"
            "/vkreply VK_ID текст ответа\n\n"
            "Пример:\n"
            "/vkreply 123456789 Здравствуйте, заказ приняли."
        )
        return

    parts = command.args.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Нужно указать VK ID и текст ответа.\n\n"
            "Пример:\n"
            "/vkreply 123456789 Здравствуйте, заказ приняли."
        )
        return

    vk_user_id = parts[0]
    reply_text = parts[1]

    vk_token = os.getenv("VK_TOKEN")

    async with ClientSession() as session:
        async with session.post(
            "https://api.vk.com/method/messages.send",
            data={
                "access_token": vk_token,
                "user_id": vk_user_id,
                "message": reply_text,
                "random_id": 0,
                "v": "5.199"
            }
        ) as response:
            result = await response.json()

    if "error" in result:
        await message.answer(f"❌ Ошибка VK:\n{result['error']}")
        return

    await message.answer("✅ Ответ отправлен в VK.")

@router.message()
async def receive_order(message: Message):
    if not message.text:
        await message.answer("Пожалуйста, отправьте заказ текстовым сообщением.")
        return

    if message.text in [
        "📋 Прайс лист",
        "🛒 Сделать заказ",
        "🚚 Информация по доставке",
        "☎️ Связаться с менеджером"
    ]:
        return

    text = message.text.strip().lower()

    if len(text) < 10 or text in ["привет", "здравствуйте", "ок", "спасибо"]:
        await message.answer(
            "Пожалуйста, нажмите «🛒 Сделать заказ» и отправьте заказ одним сообщением.",
            reply_markup=main_keyboard
        )
        return

    username = message.from_user.username
    username_text = f"@{username}" if username else "username не указан"
    save_order(
    source="Telegram",
    order_text=message.text,
    client_username=username_text,
    client_id=message.from_user.id,
    client_name=message.from_user.full_name
    )
    text = (
        "🆕 Новый заказ:\n\n"
        f"{message.text}\n\n"
        f"Telegram клиента: {username_text}\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Имя в Telegram: {message.from_user.full_name}"
    )

    await message.bot.send_message(ADMIN_ID, text)

    await message.answer(
        "✅ Заказ принят!\n\n"
        "Мы получили вашу заявку.\n"
        "Свяжемся с вами в ближайшее время.\n\n"
        "Спасибо 🙌",
        reply_markup=main_keyboard
    )
