import asyncio
import logging

from aiogram import Dispatcher
from src.bot.config import bot
from src.bot.handlers.home import router as home_router
from src.bot.handlers.system import router as system_router


async def main():
    dp = Dispatcher()
    dp.include_router(home_router)
    dp.include_router(system_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())