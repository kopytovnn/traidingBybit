import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from multiprocessing import Process

# from bingx_w.main import work as bing_x_start
from bybit_release import main as bybit

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6437889245:AAFqZXpbh9iu4tvl9fNIu1QvEbjWa6cWkKA"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"""Отправьте сообщение в формате:\napikey\nsecretkey\ndeposit""")


@dp.message()
async def cmd_test2(message: Message):
    try:
        # print(message.text)
        cds = message.text.split('\n')
        # print('\r', cds)
        api_key, secret_key, deposit = cds
        p1 = Process(target=bybit.start, args=(api_key, secret_key, float(deposit)))
        p1.start()
        # bybit.start(api_key, secret_key, float(deposit))
        await message.reply("BybBit has been started")
    except BaseException as e:
        print(e)
        await message.reply("Ошибка")


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        # Send a copy of the received message
        # print(message)
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())