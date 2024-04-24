from fix.bybit_release.Dispatcher import *
from fix.bybit_release.config import *


async def start(apikey, secretkey, symbol, deposit):
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    await dp.upd_v6()