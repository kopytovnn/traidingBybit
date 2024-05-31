import asyncio
from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup
from app.keyboards.simple_row import make_row_keyboard, make_inline_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards import buttons

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# from ..database.models import user
from database.models import user
from msgs import msgs
from app.keyboards import buttons


engine = create_engine("sqlite:///Data.db", echo=True)


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
tasks = {}


class ByBitStart(StatesGroup):
    uid = State()
    symbol = State()
    deposit = State()
    stop = State()
    gofromadding = State()


@router.message(Command("all_users"))
@router.callback_query(F.data == "all_users")
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    with Session(engine) as session:
        all_users = session.query(user.User).all()
        textanswer = ""
        for u in all_users:
            textanswer += msgs.useroutput(u) + '\n'

        await callback.message.answer(
            text=msgs.useroutput(u),
        )
        await callback.message.answer(
            text="Введите порядковый номер пользователя"
        )
    await state.set_state(ByBitStart.uid.state)

@router.message(ByBitStart.uid)
async def bybitdeposiot(message: types.Message, state: FSMContext):
    await state.update_data(uid=int(message.text.lower()))
    user_data = await state.get_data()
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(user_data["uid"])).all()[0]
        await message.answer(text=msgs.userbigouput(u))


@router.callback_query(F.data.startswith("bybit_start_"))
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(uid=callback.data.split('_')[2])


@router.callback_query(F.data.startswith("bybit_stop_"))
async def stopany(callback: types.CallbackQuery, state: FSMContext):
    uid=callback.data.split('_')[2]
    tasks[uid].terminate()
    await callback.message.answer("ByBit останвлен")


@router.callback_query(F.data.startswith("bybit_start_"))
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(uid=callback.data.split('_')[2])

    await callback.message.answer("Введите торговую пару", reply_markup=make_inline_keyboard(coins))
    await state.set_state(ByBitStart.symbol.state)


@router.message(ByBitStart.symbol)
@router.callback_query(F.data.startswith("bybit_change_"))
async def bybitsymbol(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(symbol=callback.data.split('_')[2])

    await state.set_state(ByBitStart.deposit.state)
    await callback.message.answer("Введите желаемый депозит в usdt")


@router.message(ByBitStart.deposit)
async def bybitdeposiot(message: types.Message, state: FSMContext):
    from multiprocessing import Process
    from fix.Bybit.main import start

    await state.update_data(deposit=message.text.lower())

    user_data = await state.get_data()

    # uid, symbol, deposit = user_data.values()
    uid = user_data["uid"]
    symbol = user_data["symbol"]
    deposit = user_data["deposit"]
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(uid)).all()[0]
        apikey, secretkey = u.bybitapi, u.bybitsecret
        print(apikey, secretkey)
        p = Process(target=start, args=(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit)))
        p.daemon = True
        p.start()
        tasks[uid] = p
        await message.reply("BybBit запущен")    


def register_handlers_bybit_start(dp: Dispatcher):
    dp.register_message_handler(allusers, commands="/all_users", state="*")
    # dp.register_message_handler(bybitstart, state=ByBitStart.uid)
    # dp.register_message_handler(aaa, sta)
    dp.register_message_handler(allusers_alt, State=ByBitStart.gofromadding)
    dp.register_message_handler(bybitsymbol, state=ByBitStart.symbol)
    dp.register_message_handler(bybitdeposiot, state=ByBitStart.deposit)
    # dp.register_message_handler(bybit_symbol_chosen, state=BybitAuthData.waiting_for_symbol)
    # dp.register_message_handler(bybit_deposiot_chosen, state=BybitAuthData.waiting_for_deposit)