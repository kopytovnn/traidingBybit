from fix.Bybit.bybitAPI import Client
from fix.Bybit.Order import *
from fix.Bybit.Position import *
from fix.Bybit.config import *


symbol = 'DOGEUSDT'
leverage = 20

cl = Client(API_KEY, SECRET_KEY)
# cl.switch_position_mode(symbol, 3)

status = 'Sell'
try:
    print(cl.market_tp(symbol, 0.14110, 2))
except:
    print(cl.market_tp(symbol, 0.14110, 1))