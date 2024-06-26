from fix.Bybit.Order import *
from fix.Bybit.bybitAPI import *
from fix.Bybit.config import *
from fix.Bybit.Dispatcher2 import Dispatcher
import asyncio


def start(apikey, secretkey, symbol, deposit, uid=None, coef=None):
    print(apikey, secretkey, symbol, deposit)
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit, uid=uid)
    if coef:
        for i in dp.stepMap:
            dp.valueMap[i] *= float(coef)
    print('start')
    asyncio.run(dp.asyncEngineStart())


# start(API_KEY, SECRET_KEY, 'XRPUSDT', 500)
