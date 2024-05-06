from fix.Bybit.Order import *
from fix.Bybit.bybitAPI import *
from fix.Bybit.config import *
from fix.Bybit.Dispatcher2 import Dispatcher
import asyncio


def start():
    cl = Client(API_KEY, SECRET_KEY)
    dp = Dispatcher(cl, 'XRPUSDT', 20, 5000)
    asyncio.run(dp.asyncEngineStart())
