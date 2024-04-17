from bingxAPI import Client
from Dispatcher_v2 import Dispatcher
import config


async def work(api_key, secret_key, symbol, leverage):
    cl = Client(api_key, secret_key)
    dp = Dispatcher(cl=cl,
                    symbol=symbol,
                    leverage=leverage)


if __name__ == '__main__':
    cl = Client(config.APIKEY, config.SECRETKEY)
    dp = Dispatcher(cl=cl,
                    symbol='SOL-USDT',
                    leverage=20)

    dp.work()

