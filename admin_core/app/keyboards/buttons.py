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

PERSONAL_ACCOUNT = types.InlineKeyboardButton(
        text="Личный кабинет",
        callback_data="account")


def COIN(coin):
    return types.InlineKeyboardButton(
        text=coin,
        callback_data=f"bybit_change_{coin}")


def CHANGE_END_DATE(id1):
    return types.InlineKeyboardButton(
        text='Смена даты',
        callback_data=f"changeenddate_{id1}"
    )