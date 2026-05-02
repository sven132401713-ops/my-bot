from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Прайс лист")],
        [KeyboardButton(text="🛒 Сделать заказ")],
        [KeyboardButton(text="🚚 Информация по доставке")],
    ],
    resize_keyboard=True
)


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я помогу оформить заказ.\n\n"
        "Выберите нужный раздел:",
        reply_markup=main_keyboard
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Доступные разделы:\n"
        "📋 Прайс лист\n"
        "🛒 Сделать заказ\n"
        "🚚 Информация по доставке"
    )


@router.message(Command("info"))
async def info_handler(message: Message):
    await message.answer("Я бот для приёма заказов.")


@router.message(F.text == "📋 Прайс лист")
async def price_handler(message: Message):
    await message.answer(
        "📋 Прайс лист:\n\n"
        "1. Товар 1 — 1000 ₽\n"
        "2. Товар 2 — 1500 ₽\n"
        "3. Товар 3 — 2000 ₽\n\n"
        "Для заказа нажмите «🛒 Сделать заказ»."
    )


@router.message(F.text == "🚚 Информация по доставке")
async def delivery_handler(message: Message):
    await message.answer(
        "🚚 Информация по доставке:\n\n"
        "Доставка осуществляется по Самаре и Новокуйбышевску.\n"
        "Дни доставки: вторник и пятница.\n"
        "Минимальный заказ 1000 рублей. При заказе от 1000 до 2500 рублей доставка 150 рублей, при заказе от 2500 рублей доставка бесплатная."
    )


@router.message(F.text == "🛒 Сделать заказ")
async def order_handler(message: Message):
    await message.answer(
        "🛒 Чтобы оформить заказ, напишите одним сообщением:\n\n"
        "1. Что хотите заказать\n"
        "2. Количество\n"
        "3. Ваше имя\n"
        "4. Телефон\n"
        "5. Адрес доставки\n\n"
        "Пример:\n"
        "Товар 1, 2 кг, Иван, +79991234567, Самара, ул. Ленина 1"
    )
