from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiohttp import ClientSession
from bot.database import save_order, get_all_orders, get_stats
from bot.ai_helper import ask_ai
import os

router = Router()

ADMIN_ID = 5876599297


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Прайс лист")],
        [KeyboardButton(text="🥛 Каталог")],
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
@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = get_stats()

    text = (
        f"📊 Статистика\n\n"
        f"📦 Всего заказов: {stats['total']}\n"
        f"✈ Telegram: {stats['telegram']}\n"
        f"📘 VK: {stats['vk']}"
    )

    await message.answer(text)    
@router.message(Command("orders"))
async def show_orders(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    orders = get_all_orders()

    if not orders:
        await message.answer("Заказов пока нет.")
        return

    text = "📦 Последние заказы:\n\n"

    for order in orders[:10]:
        text += (
            f"#{order[0]}\n"
            f"Дата: {order[1]}\n"
            f"Источник: {order[2]}\n"
            f"Заказ: {order[3]}\n"
            f"Клиент: {order[4]}\n\n"
        )

    await message.answer(text)
@router.message(F.text == "🥛 Каталог")
async def catalog_handler(message: Message):

    catalog_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🥛 Молочная продукция")],
            [KeyboardButton(text="🥟 Полуфабрикаты")],
            [KeyboardButton(text="🥫 Домашняя консервация")],
            [KeyboardButton(text="⭐ Отзывы")],
            [KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Выберите категорию:",
        reply_markup=catalog_keyboard
    )
@router.message(F.text == "🥛 Молочная продукция")
async def dairy_handler(message: Message):
    await message.answer(
        "🥛 Молочная продукция:\n\n"
        "• Сметана\n"
        "• Творог\n"
        "• Брынза\n\n"
        "📋 Актуальные цены смотрите в разделе «Прайс лист».\n"
        "🛒 Для заказа нажмите «Сделать заказ»"
    )


@router.message(F.text == "🥟 Полуфабрикаты")
async def semi_finished_handler(message: Message):
    await message.answer(
        "🥟 Полуфабрикаты:\n\n"
        "• Пельмени свинина/говядина\n"
        "• Пельмени куриные\n"
        "• Манты свинина/говядина\n"
        "• Манты куриные\n"
        "• Манты с горбушей\n"
        "• Вареники с картофелем\n"
        "• Вареники с грибами/картофелем\n"
        "• Котлеты свинина/говядина\n"
        "• Котлеты с горбушей\n"
        "• Голубцы ленивые\n"
        "• Голубцы свинина/говядина\n"
        "• Перец фаршированный\n"
        "• Люля-кебаб свинина/говядина\n"
        "• Люля-кебаб свинина/курица\n"
        "• Сырники классические\n"
        "• Блины с фаршем\n"
        "• Блины курица/грибы\n"
        "• Блины с творогом\n"
        "• Блины ветчина/сыр\n"
        "• Купаты свинина\n"
        "• Купаты курица\n\n"
        "📋 Актуальные цены смотрите в разделе «Прайс лист».\n"
        "🛒 Для заказа нажмите «Сделать заказ»"
    )


@router.message(F.text == "🥫 Домашняя консервация")
async def canned_handler(message: Message):
    await message.answer(
        "🥫 Домашняя консервация:\n\n"
        "• Домашняя тушёнка свинина\n"
        "• Домашняя тушёнка курица\n\n"
        "📋 Актуальные цены смотрите в разделе «Прайс лист».\n"
        "🛒 Для заказа нажмите «Сделать заказ»"
    )


@router.message(F.text == "⭐ Отзывы")
async def reviews_handler(message: Message):
    await message.answer(
        "⭐ Отзывы клиентов скоро добавим.\n\n"
        "Пока можете посмотреть актуальный прайс и оформить заказ.",
        reply_markup=main_keyboard
    )


@router.message(F.text == "⬅ Назад")
async def back_handler(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_keyboard
    )    
@router.message()
async def receive_order(message: Message):
    if not message.text:
        await message.answer("Пожалуйста, отправьте заказ текстовым сообщением.")
        return

    if message.text in [
        "📋 Прайс лист",
        "🛒 Сделать заказ",
        "🚚 Информация по доставке",
        "☎️ Связаться с менеджером",
        "🥛 Каталог",
        "🥛 Молочная продукция",
        "🥟 Полуфабрикаты",
        "🥫 Домашняя консервация",
        "⭐ Отзывы",
        "⬅ Назад"
    ]:
        return

    original_text = message.text
    text_lower = original_text.strip().lower()

    if len(text_lower) < 10 or text_lower in ["привет", "здравствуйте", "ок", "спасибо"]:
        await message.answer(
            "Пожалуйста, нажмите «🛒 Сделать заказ» и отправьте заказ одним сообщением.",
            reply_markup=main_keyboard
        )
        return

    ai_keywords = [
        "что",
        "посоветуй",
        "есть",
        "какие",
        "сколько",
        "подойдет",
        "подойдёт",
        "детям",
        "ужин",
        "завтрак"
    ]

    if any(word in text_lower for word in ai_keywords):
        answer = await ask_ai(original_text)

        await message.answer(
            answer,
            reply_markup=main_keyboard
        )
        return

    username = message.from_user.username
    username_text = f"@{username}" if username else "username не указан"

    save_order(
        source="Telegram",
        order_text=original_text,
        client_username=username_text,
        client_id=message.from_user.id,
        client_name=message.from_user.full_name
    )

    order_text = (
        "🆕 Новый заказ:\n\n"
        f"{original_text}\n\n"
        f"Telegram клиента: {username_text}\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Имя в Telegram: {message.from_user.full_name}"
    )

    await message.bot.send_message(ADMIN_ID, order_text)

    await message.answer(
        "✅ Заказ принят!\n\n"
        "Мы получили вашу заявку.\n"
        "Свяжемся с вами в ближайшее время.\n\n"
        "Спасибо 🙌",
        reply_markup=main_keyboard
    )