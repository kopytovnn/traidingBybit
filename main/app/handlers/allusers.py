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
from fix.Bybit import Dispatcher, TradeInfo

from multiprocessing import Process



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
    beforedate = State()
    afterdate = State()
    statistics = State()


@router.message(Command("all_users"))
@router.callback_query(F.data == "all_users")
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    with Session(engine) as session:
        all_users = session.query(user.User).all()
        textanswer = ""
        print(all_users)
        for u in all_users:
            textanswer += msgs.useroutput(u) + '\n'

        await callback.message.answer(
            text=textanswer,
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
        ti = TradeInfo.SmallBybit(u.bybitapi, u.bybitsecret)
        ti.update()

        builder = InlineKeyboardBuilder()
        builder.add(buttons.TRAIDING_PAIRS(u.id))
        builder.add(buttons.STATISTIS)
        await message.answer(text=msgs.userbigouput(u, ti),
                             reply_markup=builder.as_markup())
        
        
async def bybitdeposiotclone(message: types.Message, state: FSMContext):
    # await state.update_data(uid=int(uid))
    user_data = await state.get_data()
    print(user_data)
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(user_data["uid"])).all()[0]
        ti = TradeInfo.SmallBybit(u.bybitapi, u.bybitsecret)
        ti.update()

        builder = InlineKeyboardBuilder()
        builder.add(buttons.TRAIDING_PAIRS(u.id))
        await message.answer(text=msgs.userbigouput(u, ti),
                             reply_markup=builder.as_markup())
        

async def bybitdeposiotcloneCB(callback: types.CallbackQuery, state: FSMContext):
    # await state.update_data(uid=int(uid))
    user_data = await state.get_data()
    print(user_data)
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(user_data["uid"])).all()[0]
        ti = TradeInfo.SmallBybit(u.bybitapi, u.bybitsecret)
        ti.update()

        builder = InlineKeyboardBuilder()
        builder.add(buttons.TRAIDING_PAIRS(u.id))
        await callback.message.answer(text=msgs.userbigouput(u, ti),
                             reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("traiding_pairs_"))
async def traidingpairs2(callback: types.CallbackQuery, state: FSMContext):
    print(state.get_data, callback.data.split('_')[2])
    user_data = await state.get_data()
    print(user_data)
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(callback.data.split('_')[2])).all()[0]
        builder = InlineKeyboardBuilder()
        builder.add(buttons.COIN1(u.symbol))
        await state.set_state(ByBitStart.symbol)
        await callback.message.answer(text="Выберите активную пару",
                                      reply_markup=builder.as_markup())
        


@router.callback_query(F.data.startswith("bybit_start_"))
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(uid=callback.data.split('_')[2])
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == int(callback.data.split('_')[2])).all()[0]
        user_data = await state.get_data()

        from fix.Bybit.main import start

        p = Process(target=start, args=(str(u.bybitapi), str(u.bybitsecret), user_data["symbol"] + 'USDT', float(u.deposit)))
        p.daemon = True
        # args=(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit))
        p.start()
        tasks[u.id] = p

        from app.handlers.allusers import bybitdeposiotclone
        await bybitdeposiotcloneCB(callback, state)

    

@router.callback_query(F.data.startswith("bybit_stop_"))
async def stopany(callback: types.CallbackQuery, state: FSMContext):
    uid=int(callback.data.split('_')[2])
    tasks[uid].terminate()
    await callback.message.answer("ByBit останвлен")


@router.callback_query(F.data.startswith("bybit_stopclose_"))
async def stopclose(callback: types.CallbackQuery, state: FSMContext):
    uid=int(callback.data.split('_')[2])
    tasks[uid].terminate()
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == uid).all()[0]
        ti = TradeInfo.SmallBybit(u.bybitapi, u.bybitsecret)
        ti.endnclose(u.symbol + 'USDT')
    await callback.message.answer("ByBit останвлен. Позиции закрыты")


@router.callback_query(F.data == "get_stat")
async def aaa(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введите дату ОТ"
    )
    await state.set_state(ByBitStart.beforedate)


@router.message(ByBitStart.beforedate)
async def namechoosen(message: types.Message, state: FSMContext):
    await state.update_data(beforedate1=message.text)

    await state.set_state(ByBitStart.afterdate.state)
    await message.answer("Введите дату ДО")

@router.message(ByBitStart.afterdate)
async def namechoosen(message: types.Message, state: FSMContext):
    await state.update_data(aterdate1=message.text)
    user_data = await state.get_data()
    uid = int(user_data['uid'])
    with Session(engine) as session:
        u = session.query(user.User).filter(user.User.id == uid).all()[0]
        ti = TradeInfo.SmallBybit(u.bybitapi, u.bybitsecret)
        ti.statistics(u.symbol + 'USDT')
        from aiogram.types import FSInputFile

        doc = FSInputFile(path='C:/Users/Коля/PycharmProjects/tradeBot/out.csv', filename='out.csv')
        await message.answer_document(document=doc)
        print(user_data)


@router.callback_query(F.data.startswith("bybit_start_"))
async def allusers(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(uid=callback.data.split('_')[2])

    await callback.message.answer("Введите торговую пару", reply_markup=make_inline_keyboard(coins))
    await state.set_state(ByBitStart.symbol.state)


@router.message(ByBitStart.symbol)
@router.callback_query(F.data.startswith("bybit_change1_"))
async def bybitsymbol(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(symbol=callback.data.split('_')[2])

    user_data = await state.get_data()
    print(user_data)
    builder = InlineKeyboardBuilder()
    builder.add(buttons.STARTBYBIT(user_data["uid"]))
    builder.add(buttons.STOPBYBIT(user_data["uid"]))
    builder.add(buttons.STOPCLOSEBYBIT(user_data["uid"]))
    builder.add(buttons.CHANGE_API)
    builder.add(buttons.CHANGE_DEPOSIT)

    # await state.set_state(ByBitStart.deposit.state)
    await callback.message.answer(
        text=f"""
Торговые пары
Выбрана торговая пара: {user_data["symbol"]}
""",
    reply_markup=builder.as_markup()
    )

@router.message(Command("change_api"))
@router.callback_query(F.data == "change_api")
async def change_api(callback: types.CallbackQuery, state: FSMContext):
    from app.handlers.adduser import namechosenclone
    with Session(engine) as session:
        user_data = await state.get_data()
        u = session.query(user.User).filter(user.User.id == int(user_data["uid"])).all()[0]
        await namechosenclone(u.name, callback, state)

@router.message(Command("change_deposit"))
@router.callback_query(F.data == "change_deposit")
async def change_api(callback: types.CallbackQuery, state: FSMContext):
    from app.handlers.adduser import bybitsymbolclone
    with Session(engine) as session:
        user_data = await state.get_data()
        # u = session.query(user.User).filter(user.User.id == int(user_data["uid"])).all()[0]
        await bybitsymbolclone(callback, state)


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