from bingx_w.bingxAPI import Client
from bingx_w.Dispatcher_v2 import Dispatcher
import bingx_w.config


async def work(api_key, secret_key, symbol, leverage):
    cl = Client(api_key, secret_key)
    dp = Dispatcher(cl=cl,
                    symbol=symbol,
                    leverage=leverage)
    dp.work()

# if __name__ == '__main__':
#     cl = Client(config.APIKEY, config.SECRETKEY)
#     dp = Dispatcher(cl=cl,
#                     symbol='SOL-USDT',
#                     leverage=5)
#
#     dp.work()

