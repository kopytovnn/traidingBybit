from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from app.keyboards.simple_row import make_row_keyboard


router = Router()


class BybitAuthData(StatesGroup):
    waiting_for_apikey = State()
    waiting_for_secretkey = State()
    waiting_for_symbol = State()
    waiting_for_deposit = State()


@router.message(Command("bybit_start"))
async def bybit_auth_start(message: types.Message, state: FSMContext):
    await message.answer("Введите apikey")
    await state.set_state(BybitAuthData.waiting_for_apikey.state)


@router.message(BybitAuthData.waiting_for_apikey)
async def bybit_apikey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(apikey=message.text.lower())

    await state.set_state(BybitAuthData.waiting_for_secretkey.state)
    await message.answer("Теперь введите secretkey")


@router.message(BybitAuthData.waiting_for_secretkey)
async def bybit_secretkey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(secretkey=message.text.lower())

    await state.set_state(BybitAuthData.waiting_for_symbol.state)
    await message.answer("Введите торговую пару", reply_markup=make_row_keyboard(['XRP', 'SOL', 'ETH', 'NEAR']))


@router.message(BybitAuthData.waiting_for_symbol)
async def bybit_symbol_chosen(message: types.Message, state: FSMContext):
    await state.update_data(symbol=message.text.lower())

    await state.set_state(BybitAuthData.waiting_for_deposit.state)
    await message.answer("Введите желаемый депозит в usdt")


@router.message(BybitAuthData.waiting_for_deposit)
async def bybit_deposiot_chosen(message: types.Message, state: FSMContext):
    await state.update_data(deposit=message.text.lower())

    user_data = await state.get_data()
    print(user_data)

    


def register_handlers_bybit_auth(dp: Dispatcher):
    dp.register_message_handler(bybit_auth_start, commands="/bybit_auth", state="*")
    dp.register_message_handler(bybit_apikey_chosen, state=BybitAuthData.waiting_for_apikey)
    dp.register_message_handler(bybit_secretkey_chosen, state=BybitAuthData.waiting_for_secretkey)
    dp.register_message_handler(bybit_symbol_chosen, state=BybitAuthData.waiting_for_symbol)
    dp.register_message_handler(bybit_deposiot_chosen, state=BybitAuthData.waiting_for_deposit)

