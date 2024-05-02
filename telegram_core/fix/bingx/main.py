from fix.bingx.Dispatcher import *
# from config import *
from fix.bingx.config import *


def start(apikey, secretkey, symbol, deposit):
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    # asyncio.run(dp.upd())
    # dp.upd()
    dp.upd_unite()


# if __name__ == '__main__':
#     start(apikey=APIKEY, secretkey=SECRETKEY, symbol='XRP-USDT', deposit=5000)