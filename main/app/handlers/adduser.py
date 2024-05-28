import asyncio
from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup

from app.keyboards import buttons

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# from ..database.models import user
from database.models import user


engine = create_engine("sqlite:///Data.db", echo=True)


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
bingx_tasks = {}


class AddNewUser(StatesGroup):
    name = State()
    bybitapi = State()
    bybitsecret = State()

@router.message(Command("add_user"))
@router.callback_query(F.data == "add_user")
async def adduser(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введите имя пользователя:"
    )
    await state.set_state(AddNewUser.name)


@router.message(AddNewUser.name)
async def namechoosen(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await state.set_state(AddNewUser.bybitapi.state)
    await message.answer("Введите API key пользователя от ByBit")


@router.message(AddNewUser.bybitapi)
async def bybitapichoosen(message: types.Message, state: FSMContext):
    await state.update_data(bybitapi=message.text)

    await state.set_state(AddNewUser.bybitsecret)
    await message.answer("Введите Secret key пользователя от ByBit")


@router.message(AddNewUser.bybitsecret)
async def bybitsecretchoosen(message: types.Message, state: FSMContext):
    await state.update_data(bybitsecret=message.text)
    user_data = await state.get_data()

    with Session(engine) as session:
        nu = user.User(name=user_data["name"],
                       bybitapi=user_data["bybitapi"],
                       bybitsecret=user_data["bybitsecret"])
        session.add_all([nu,])
        session.commit()
    
    await message.answer("Данные успешно вынесены")

    # await message.answer("Данные внесены")



def register_handlers_bybit_auth(dp: Dispatcher):
    dp.register_message_handler(adduser, commands="/add_user", state="*")
    dp.register_message_handler(namechoosen, state=AddNewUser.name)
    dp.register_message_handler(bybitapichoosen, state=AddNewUser.bybitapi)
    dp.register_message_handler(bybitsecretchoosen, state=AddNewUser.bybitsecret)