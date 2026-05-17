import asyncio
import logging
import os
from bot.database import init_db
from aiogram import Bot, Dispatcher
from bot.handlers import router
from bot.vk_handler import setup_vk_app
from aiohttp import web


async def main():
    init_db()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    dp.include_router(router)

    # Telegram polling
    asyncio.create_task(dp.start_polling(bot))

    # VK webhook server
    app = setup_vk_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    # держим процесс живым
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
