import asyncio
from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup

from app.keyboards.simple_row import make_row_keyboard, make_inline_keyboard_BINGX
from app.keyboards import buttons

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# from ..database.models import user
from app.handlers.fix.db.models import user


engine = create_engine("sqlite:///Data.db", echo=True)


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
bingx_tasks = {}


class AddNewUser(StatesGroup):
    waiting_for_tg = State()
    waiting_for_enddate = State()

@router.message(Command("add_user"))
@router.callback_query(F.data == "add_user")
# @router.message(StateFilter(None), Command("add_user"))
async def cmd_food(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введите tg id:"
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(AddNewUser.waiting_for_tg)


@router.message(AddNewUser.waiting_for_tg)
async def bybit_apikey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(tg=message.text)

    await state.set_state(AddNewUser.waiting_for_enddate.state)
    await message.answer("Теперь введите дату окончания подписки в формате XX.XX.XXXX")


@router.message(AddNewUser.waiting_for_enddate)
async def bybit_deposiot_chosen(message: types.Message, state: FSMContext):
    await state.update_data(enddate=message.text.lower())

    user_data = await state.get_data()

    with Session(engine) as session:
        nu = user.User(telegram_id=user_data["tg"],
                       enddate=user_data["enddate"])
        session.add_all([nu,])
        session.commit()

    await message.answer("Данные внесены")



def register_handlers_bybit_auth(dp: Dispatcher):
    dp.register_message_handler(cmd_food, commands="/add_user", state="*")
    dp.register_message_handler(bybit_apikey_chosen, state=AddNewUser.waiting_for_tg)
    dp.register_message_handler(bybit_deposiot_chosen, state=AddNewUser.waiting_for_enddate)