from bybit_release.Dispatcher import *


async def start(apikey, secretkey, deposit):
    cl = Client(apikey, secretkey)

    symbol = 'XRPUSDT'
    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    await dp.upd_v6()
