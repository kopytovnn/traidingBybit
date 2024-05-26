import asyncio
from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.simple_row import make_row_keyboard, make_inline_keyboard_BINGX
from app.keyboards import buttons

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
# from ..database.models import user
from app.handlers.fix.db.models import user
from app.handlers import msgs 

import app.keyboards.buttons as my_buttons


engine = create_engine("sqlite:///Data.db", echo=True)


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
bingx_tasks = {}


class AllUsers(StatesGroup):
    waiting_for_action = State()
    waiting_for_enddate = State()

@router.message(Command("all_users"))
@router.callback_query(F.data == "all_users")
# @router.message(StateFilter(None), Command("add_user"))
async def cmd_food(callback: types.CallbackQuery, state: FSMContext):
    with Session(engine) as session:
        all_users = session.query(user.User).all()
        for u in all_users:
            builder = InlineKeyboardBuilder()
            builder.add(my_buttons.CHANGE_END_DATE(u.id))

            await callback.message.answer(
                text=msgs.UserInfoMsg(u.id, u.telegram_id, u.enddate),
                reply_markup=builder.as_markup()
            )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(AllUsers.waiting_for_action)

@router.message(AllUsers.waiting_for_action)
@router.callback_query(F.data.startswith("changeenddate_"))
async def changeenddate(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(symbol=callback.data.split('_')[1])
    await state.set_state(AllUsers.waiting_for_enddate)
    await callback.message.answer(text='Введите новую дату')

@router.message(AllUsers.waiting_for_enddate)
async def changeenddate(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    with Session(engine) as session:
        print(f'\t\t\t\t\t{message.text}')
        user1 = session.query(user.User).filter(user.User.id == int(user_data['symbol']))
        # print(user1.__dict__, user1.all()[0].__dict__)
        user1.all()[0].enddate = message.text
        session.commit()
    await message.answer('Данные успешно внесены')


def register_handlers_bybit_auth(dp: Dispatcher):
    dp.register_message_handler(cmd_food, commands="/all_users", state="*")