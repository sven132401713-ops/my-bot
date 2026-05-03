from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, ReplyKeyboardRemove
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


# КНОПКИ
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Прайс лист")],
        [KeyboardButton(text="🛒 Сделать заказ")],
        [KeyboardButton(text="🚚 Информация по доставке")],
    ],
    resize_keyboard=True
)
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отменить заказ")]
    ],
    resize_keyboard=True
)

# FSM СОСТОЯНИЯ
class OrderState(StatesGroup):
    product = State()
    quantity = State()
    name = State()
    phone = State()
    address = State()


ADMIN_ID = 5876599297
@router.message(F.text == "❌ Отменить заказ")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Заказ отменён.",
        reply_markup=main_keyboard
    )

# СТАРТ
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Выберите действие:",
        reply_markup=main_keyboard
    )


# ПРАЙС
@router.message(F.text == "📋 Прайс лист")
async def price_handler(message: Message):
    import os

    await message.answer("📋 Отправляю прайс лист:")

    base_dir = os.path.abspath(os.path.join(os.getcwd(), "images"))

    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price1.png")))
    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price2.png")))
    await message.answer_photo(FSInputFile(os.path.join(base_dir, "price3.png")))

    await message.answer("Для заказа нажмите «🛒 Сделать заказ».")

# ДОСТАВКА
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
        "От 2500 — доставка бесплатная."
    )


# СТАРТ ЗАКАЗА
@router.message(F.text == "🛒 Сделать заказ")
async def order_start(message: Message, state: FSMContext):
    await message.answer("Что хотите заказать?", reply_markup=cancel_keyboard)
    await state.set_state(OrderState.product)


# ШАГ 1
@router.message(OrderState.product)
async def order_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer("Какое количество?", reply_markup=cancel_keyboard)
    await state.set_state(OrderState.quantity)


# ШАГ 2
@router.message(OrderState.quantity)
async def order_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer("Ваше имя?", reply_markup=cancel_keyboard)
    await state.set_state(OrderState.name)


# ШАГ 3
@router.message(OrderState.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Отправить номер", request_contact=True)]
        ],
    )

    await message.answer(
        "Отправьте ваш номер телефона:",
        reply_markup=phone_keyboard, reply_markup=cancel_keyboard
    )

    await state.set_state(OrderState.phone)


# ШАГ 4
@router.message(OrderState.phone)
async def order_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)
    await message.answer("Адрес доставки?", reply_markup=main_keyboard, reply_markup=cancel_keyboard)
    await state.set_state(OrderState.address)


# ШАГ 5 (ФИНАЛ)
@router.message(OrderState.address)
async def order_finish(message: Message, state: FSMContext):
    data = await state.get_data()

    username = message.from_user.username
    username_text = f"@{username}" if username else "username не указан"

    text = (
        "🆕 Новый заказ:\n\n"
        f"Товар: {data['product']}\n"
        f"Количество: {data['quantity']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {message.text}\n\n"
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

    await state.clear()