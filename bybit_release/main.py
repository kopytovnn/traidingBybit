from bybit_release.Dispatcher import *


def start(apikey, secretkey, deposit):
    cl = Client(apikey, secretkey)

    symbol = 'ETHUSDT'
    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    dp.upd_v5()
