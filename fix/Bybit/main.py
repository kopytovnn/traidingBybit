from fix.Bybit.Order import *
from fix.Bybit.bybitAPI import *
from fix.Bybit.config import *
from fix.Bybit.Dispatcher2 import Dispatcher
import asyncio


def start(apikey, secretkey, symbol, depo):
    cl = Client(apikey, secretkey)
    dp = Dispatcher(cl, symbol, 20, depo)
    asyncio.run(dp.asyncEngineStart())
