from fix.Bybit.bybitAPI import Client
from fix.Bybit.config import *


cl = Client(API_KEY, SECRET_KEY)
cl.switch_position_mode("MANAUSDT", 3)
resp = cl.position_size_sell("MANAUSDT")

status = 'Sell'
d = {'Sell': 2, 'Buy': 1}
for pos in resp['result']['list']:
    if pos['positionIdx'] == d[status]:
        psize = pos['size']
        if psize != "0":
            cl.market_close_short('MANAUSDT', psize)

status = 'Buy'
for pos in resp['result']['list']:
    if pos['positionIdx'] == d[status]:
        psize = pos['size']
        if psize != "0":
            cl.market_close_long('MANAUSDT', psize)
# cl.market_close_long("MANAUSDT")