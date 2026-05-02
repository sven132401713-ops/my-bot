from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я Telegram-бот.")


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/info — информация о боте"
    )


@router.message(Command("info"))
async def info_handler(message: Message):
    await message.answer("Я минимальный Telegram-бот на Python и aiogram 3.")
