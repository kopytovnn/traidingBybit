from fix.bingx.Dispatcher import *
# from config import *
from fix.bingx.config import *

import gevent
from gevent import monkey
monkey.patch_all()


def start(apikey, secretkey, symbol, deposit):
    cl = Client(apikey, secretkey)

    leverage = 20

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    print('start')
    asyncio.run(dp.upd())




if __name__ == '__main__':
    start(apikey=APIKEY, secretkey=SECRETKEY, symbol='XRP-USDT', deposit=5000)