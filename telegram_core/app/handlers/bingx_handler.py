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

# from fix.bing.main import start as bybit_start
from fix.bingx.main import start as bingx_start


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
tasks = {}


class BingXAuthData(StatesGroup):
    waiting_for_apikey = State()
    waiting_for_secretkey = State()
    waiting_for_symbol = State()
    waiting_for_deposit = State()


@router.message(Command("bingx_start"))
@router.callback_query(F.data == "bingx_start")
async def bingx_auth_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите apikey")
    await state.set_state(BingXAuthData.waiting_for_apikey.state)


@router.message(BingXAuthData.waiting_for_apikey)
async def bingx_apikey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(apikey=message.text)

    await state.set_state(BingXAuthData.waiting_for_secretkey.state)
    await message.answer("Теперь введите secretkey")


@router.message(BingXAuthData.waiting_for_secretkey)
async def bingx_secretkey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(secretkey=message.text)

    await state.set_state(BingXAuthData.waiting_for_symbol.state)
    await message.answer("Введите торговую пару", reply_markup=make_inline_keyboard_BINGX(coins))


@router.message(BingXAuthData.waiting_for_symbol)
@router.callback_query(F.data.startswith("bingx_change_"))
async def bingx_symbol_chosen(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(symbol=callback.data.split('_')[2])

    await state.set_state(BingXAuthData.waiting_for_deposit.state)
    await callback.message.answer("Введите желаемый депозит в usdt")


@router.message(BingXAuthData.waiting_for_deposit)
async def bingx_deposiot_chosen(message: types.Message, state: FSMContext):
    await state.update_data(deposit=message.text.lower())

    user_data = await state.get_data()
    
    apikey, secretkey, symbol, deposit = user_data.values()
    print(f'\t{symbol}\n')
    task = asyncio.create_task(bingx_start(str(apikey), str(secretkey), symbol.upper() + '-USDT', float(deposit)))
    tasks[message.chat.id] = task

    await message.reply("BingX запущен", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[buttons.BINGX_STOP]]))    


@router.callback_query(F.data == "bingx_stop")
async def bingx_stop(callback: types.CallbackQuery):
    tasks[callback.message.chat.id].cancel()

    await callback.message.answer("BingX останвлен")


def register_handlers_bingx_auth(dp: Dispatcher):
    dp.register_message_handler(bingx_auth_start, commands="/bingx_auth", state="*")
    dp.register_message_handler(bingx_apikey_chosen, state=BingXAuthData.waiting_for_apikey)
    dp.register_message_handler(bingx_secretkey_chosen, state=BingXAuthData.waiting_for_secretkey)
    dp.register_message_handler(bingx_symbol_chosen, state=BingXAuthData.waiting_for_symbol)
    dp.register_message_handler(bingx_deposiot_chosen, state=BingXAuthData.waiting_for_deposit)

