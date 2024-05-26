import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import TOKEN

from app.handlers import common

from aiogram.filters import CommandStart

from aiogram.types import Message

import multiprocessing as mp


from app.handlers import add_new_user, all_users


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(TOKEN)

    dp.include_router(common.router)
    dp.include_router(add_new_user.router)
    dp.include_router(all_users.router)

    # dp.include_router(bingx_handler.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())