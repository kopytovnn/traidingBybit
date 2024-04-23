from aiogram import Bot, Dispatcher, Router, types


BYBIT_START = types.InlineKeyboardButton(
        text="Запуск Bybit",
        callback_data="bybit_start")
BINGX_START = types.InlineKeyboardButton(
        text="Запуск BingX",
        callback_data="bingx_start")
PERSONAL_ACCOUNT = types.InlineKeyboardButton(
        text="Личный кабинет",
        callback_data="account")
