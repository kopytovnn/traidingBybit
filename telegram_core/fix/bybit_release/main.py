from fix.bybit_release.Dispatcher import *


async def start(apikey, secretkey, symbol, deposit):
    print(f'apikey: "{apikey}"\nsecretkey: "{secretkey}"\nsymbol: "{symbol}"\ndeposit: "{deposit}"\n')
    cl = Client(apikey, secretkey)

    leverage = 20


    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=deposit)
    await dp.upd_v6()
