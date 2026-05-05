import asyncio
from aiogram import Bot, Dispatcher 
from bot.vk_handler import setup_vk_app
from aiohttp import web
import asyncio
from bot.config import BOT_TOKEN
from bot.handlers import router

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    dp.include_router(router)

    # запускаем Telegram
    asyncio.create_task(dp.start_polling(bot))

    # запускаем VK сервер
    app = setup_vk_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    # держим процесс
    while True:
        await asyncio.sleep(3600)
