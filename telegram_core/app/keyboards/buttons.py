from aiogram import Bot, Dispatcher, Router, types


BYBIT_START = types.InlineKeyboardButton(
        text="Запуск Bybit",
        callback_data="bybit_start")
BYBIT_STOP = types.InlineKeyboardButton(
        text="Остановка Bybit",
        callback_data="bybit_stop")

BINGX_START = types.InlineKeyboardButton(
        text="Запуск BingX",
        callback_data="bingx_start")
BINGX_STOP = types.InlineKeyboardButton(
        text="Остановка BingX",
        callback_data="bybit_stop")

PERSONAL_ACCOUNT = types.InlineKeyboardButton(
        text="Личный кабинет",
        callback_data="account")


def COIN(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bybit_change_{coin}")


def COIN_BINGX(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bingx_change_{coin}")
