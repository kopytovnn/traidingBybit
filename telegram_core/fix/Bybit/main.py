from fix.Bybit.Order import *
from fix.Bybit.bybitAPI import *
from fix.Bybit.config import *
from fix.Bybit.Dispatcher import Dispatcher
import asyncio


def start(apikey, secretkey, symbol, deposit):
    print(apikey, secretkey, symbol, deposit)
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    asyncio.run(dp.upd_v6())


# start(API_KEY, SECRET_KEY, 'XRPUSDT', 500)
