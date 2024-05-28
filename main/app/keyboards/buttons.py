from aiogram import Bot, Dispatcher, Router, types


EDIT_DATA = types.InlineKeyboardButton(
    text="Редактировать данные пользователя",
    callback_data="edit"
)

ALL_USERS = types.InlineKeyboardButton(
    text="Пользователи",
    callback_data="all_users"
)

ADD_USER = types.InlineKeyboardButton(
    text="Добавить пользователя",
    callback_data="add_user"
)

STARTBYBIT1 = types.InlineKeyboardButton(
    text="Запустить ByBit",
    callback_data="bybit_start_"
)

def STARTBYBIT(uid):
    return types.InlineKeyboardButton(
        text="Запустить ByBit",
        callback_data=f"bybit_start_{uid}"
    )

def STOPBYBIT(uid):
    return types.InlineKeyboardButton(
        text="Остановить ByBit",
        callback_data=f"bybit_stop_{uid}"
    )


def COIN(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bybit_change_{coin}")