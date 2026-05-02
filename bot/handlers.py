from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile import os
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


# FSM СОСТОЯНИЯ
class OrderState(StatesGroup):
    product = State()
    quantity = State()
    name = State()
    phone = State()
    address = State()


ADMIN_ID = 5876599297


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

    photo_path = os.path.abspath(
        os.path.join(os.getcwd(), "images", "price1.png")
    )

    if not os.path.exists(photo_path):
        await message.answer(f"⚠️ Фото не найдено: {photo_path}")
        return

    await message.answer_photo(FSInputFile(photo_path))

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
    await message.answer("Что хотите заказать?")
    await state.set_state(OrderState.product)


# ШАГ 1
@router.message(OrderState.product)
async def order_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer("Какое количество?")
    await state.set_state(OrderState.quantity)


# ШАГ 2
@router.message(OrderState.quantity)
async def order_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer("Ваше имя?")
    await state.set_state(OrderState.name)


# ШАГ 3
@router.message(OrderState.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Ваш телефон?")
    await state.set_state(OrderState.phone)


# ШАГ 4
@router.message(OrderState.phone)
async def order_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Адрес доставки?")
    await state.set_state(OrderState.address)


# ШАГ 5 (ФИНАЛ)
@router.message(OrderState.address)
async def order_finish(message: Message, state: FSMContext):
    data = await state.get_data()

    text = (
        "🆕 Новый заказ:\n\n"
        f"Товар: {data['product']}\n"
        f"Количество: {data['quantity']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {message.text}"
    )

    await message.bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заказ принят! Мы свяжемся с вами.")

    await state.clear()