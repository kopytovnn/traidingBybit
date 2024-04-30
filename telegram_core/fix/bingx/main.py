from fix.bingx.Dispatcher import *
# from config import *


def start(apikey, secretkey, symbol, deposit):
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    asyncio.run(dp.upd())