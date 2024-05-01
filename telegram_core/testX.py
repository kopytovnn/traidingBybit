from fix.bingx.main import start as bingx_start
from fix.bingx.config import *


bingx_start(apikey=APIKEY,
            secretkey=SECRETKEY,
            symbol='XRP-USDT',
            deposit=5000)