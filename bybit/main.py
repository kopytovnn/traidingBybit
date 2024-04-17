from config import *

import time
import requests
import hmac
import hashlib


SAPI = 'https://api-testnet.bybit.com'


def hashing(query_string):
    # return hmac.new(SECRET_KEY.encode('utf-8'),
    #                 query_string.encode('utf-8'),
    #                 hashlib.sha256).hexdigest()
    return hmac.new(bytes(SECRET_KEY, "utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()


def market_open_order(symbol, side, orderType, qty, category='linear'):
    url = SAPI + '/v5/order/create'
    current_time = int(time.time() * 1000)
    data = '{' + f'"symbol": "{symbol}", "side": "{side}", "orderType": "{orderType}", "qty": "{qty}", "category": "{category}"' + '}'
    sign = hashing(str(current_time) + API_KEY + '5000' + data)
    headers = {
        'X-BAPI-SIGN': sign,
        'X-BAPI-API-KEY': API_KEY,
        # 'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': str(current_time),
        'X-BAPI-RECV-WINDOW': str(5000),
        # 'Content-Type': 'application/json'
    }
    response = requests.post(url=url, headers=headers, data=data)
    print(response.text)


market_open_order(symbol='SOLUSDT', side='Sell', orderType='Market', qty=1)
