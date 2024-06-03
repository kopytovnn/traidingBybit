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

CHANGE_API = types.InlineKeyboardButton(
    text="API ключи",
    callback_data="change_api"
)

CHANGE_DEPOSIT = types.InlineKeyboardButton(
    text="Торговый депозит",
    callback_data="change_deposit"
)

STATISTIS = types.InlineKeyboardButton(
    text="Выгрузка статистики",
    callback_data="get_stat"
)

def ADD_TRAIDINGPAIR(uid):
    return types.InlineKeyboardButton(
        text="Добавить новую пару",
        callback_data=f"addtraiding_pairs_{uid}"
    )

def ACTIVE_PAIRS(uid):
    return types.InlineKeyboardButton(
        text="Активные пары",
        callback_data=f"active_pairs_{uid}"
    )

def TRAIDING_PAIRS(uid):
    return types.InlineKeyboardButton(
        text="Торговые пары",
        callback_data=f"traiding_pairs_{uid}"
    )

def STARTBYBIT(uid):
    return types.InlineKeyboardButton(
        text="Запустить",
        callback_data=f"bybit_start_{uid}"
    )

def STOPBYBIT(uid):
    return types.InlineKeyboardButton(
        text="Остановить",
        callback_data=f"bybit_stop_{uid}"
    )


def STOPCLOSEBYBIT(uid):
    return types.InlineKeyboardButton(
        text="Остановить c закрытием позиций",
        callback_data=f"bybit_stopclose_{uid}"
    )


def COIN(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bybit_change_{coin}")

def COIN1(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bybit_change1_{coin}")


