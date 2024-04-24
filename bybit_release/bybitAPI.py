from requests import get, post
from urllib.parse import urlencode

import requests
import time
import hmac
import hashlib

# import config


class Client:
    SAPI = 'https://api-testnet.bybit.com'

    def __init__(self, apikey=None, secretkey=None):
        self.apikey = apikey
        self.secretkey = secretkey

    def get_server_time(self):
        url = self.SAPI + '/v5/market/time'
        response = get(url)
        return int(response.json()['result']['timeSecond']) * 1000
        # return int(time.time() * 1000)

    def genSignature(self, payload, timeStamp, apiKey, secretKey, recvWindow):
        param_str = str(timeStamp) + apiKey + recvWindow + payload
        hash = hmac.new(bytes(secretKey, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    def _get(self, url, params=None):
        if params is None:
            params = {}
        url = self.SAPI + url
        paramsToSend = dict()
        paramsToSend['api_key'] = self.apikey
        for key in params:
            paramsToSend[key] = params[key]
        serverTime = self.get_server_time()
        paramsToSend['timestamp'] = str(serverTime)
        sortParamsToSend = dict()
        for key in sorted(paramsToSend):
            sortParamsToSend[key] = paramsToSend[key]
        paramsForHash = dict()
        for key in sortParamsToSend:
            paramsForHash[key] = sortParamsToSend[key]
        paramsForHash = urlencode(paramsForHash)
        signature = hmac.new(self.secretkey.encode('utf8'), paramsForHash.encode('utf8'), hashlib.sha256).hexdigest()
        sortParamsToSend['sign'] = signature

        response = get(url, params=sortParamsToSend, headers={})
        return response.json()

    def _post(self, url, params=None):
        if params is None:
            params = {}
        url = self.SAPI + url
        paramsToSend = dict()
        paramsToSend['api_key'] = self.apikey
        for key in params:
            paramsToSend[key] = params[key]
        serverTime = self.get_server_time()
        paramsToSend['timestamp'] = str(serverTime)
        sortParamsToSend = dict()
        for key in sorted(paramsToSend):
            sortParamsToSend[key] = paramsToSend[key]
        paramsForHash = dict()
        for key in sortParamsToSend:
            paramsForHash[key] = sortParamsToSend[key]
        paramsForHash = urlencode(paramsForHash)
        signature = hmac.new(self.secretkey.encode('utf8'), paramsForHash.encode('utf8'), hashlib.sha256).hexdigest()
        sortParamsToSend['sign'] = signature

        response = post(url, params=sortParamsToSend, headers={})
        return response.json()

    def market_tp(self, symbol, price, positionIdx):
        params = {
            "category": "linear",
            "symbol": symbol,
            "takeProfit": str(price),
            "tpTriggerBy": "MarkPrice",
            "tpslMode": "Full",
            "tpOrderType": "Market",
            "positionIdx": positionIdx
        }
        resp = self._postOrder('/v5/position/trading-stop', params)

    def _postOrder(self, url, params=None):
        if params is None:
            params = {}
        url = self.SAPI + url
        time_stamp = str(self.get_server_time())
        payload = str(params).replace("'", '"')

        recv_window = str(5000)
        signature = self.genSignature(payload, time_stamp, self.apikey, self.secretkey, recv_window)
        headers = {
            'X-BAPI-API-KEY': self.apikey,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json',
        }
        response = requests.Session().request('POST', url, headers=headers, data=payload)
        return response.json()

    def switch_position_mode(self, symbol, mode=3):
        params = {
            "category": 'linear',
            "mode": mode,
            "symbol": symbol,
        }
        resp = self._postOrder('/v5/position/switch-mode', params)
        # print(resp)

    def market_open_order(self, symbol='SOLUSDT', side='Buy', qty=10, takeProfit=-1):
        params = {"symbol": symbol,
                  "side": side,
                  "orderType": 'Market',
                  "qty": str(qty),
                  "category": 'linear',
                  # "takeProfit": str(takeProfit),
                  # "tpslMode": "Partial",
                  # "tpOrderType": "Limit",
                  # "tpLimitPrice": str(takeProfit),
                  "positionIdx": {'Sell': 2, 'Buy': 1}[side]
                  }
        resp = self._postOrder('/v5/order/create', params)
        retMsg = resp['retMsg']
        if retMsg == 'OK':
            orderId = resp['result']['orderId']
            print(f'Market order has been opened: qty = {qty}')
            return {"status": True, "orderId": orderId}
        print(resp)
        return {"status": False, "restMsg": retMsg}

    def limit_open_order(self, symbol='SOLUSDT', side='Buy', price=62000, qty=10, category='linear', takeProfit=-1):
        params = {"symbol": symbol,
                  "side": side,
                  "orderType": "Limit",
                  "qty": str(qty),
                  "category": category,
                  "price": str(price),
                  # "takeProfit": str(takeProfit),
                  # "tpslMode": "Partial",
                  # "tpOrderType": "Limit",
                  # "tpLimitPrice": str(takeProfit),
                  "positionIdx": {'Sell': 2, 'Buy': 1}[side]
                  # test
                  }
        resp = self._postOrder('/v5/order/create', params)
        retMsg = resp['retMsg']

        if retMsg == 'OK':
            print(f'Limit order has been opened: qty = {qty}, price = {price}')
            orderId = resp['result']['orderId']
            return {"status": True, "orderId": orderId}
        return {"status": False, "retMsg": retMsg}

    # def order_price(self, orderId):
    #     resp = self._get('/contract/v3/private/order/list')
    #     retMsg = resp['retMsg']
    #     if retMsg == 'OK':
    #         order_list = resp['result']['list']
    #         for order in order_list:
    #             if order['orderId'] == orderId:
    #                 return {'status': True, 'price': float(order['price']), 'orderStatus': order['orderStatus']}
    #         return {'status': False, 'retMsg': 'Order not found'}
    #     return {'status': False, 'retMsg': retMsg}
    def order_price(self, orderId):
        params = {"category": "linear",
                  "orderId": orderId}
        resp = self._get('/v5/order/realtime', params)
        retMsg = resp['retMsg']
        if retMsg == 'OK':
            order = resp['result']['list'][0]
            return {'status': True, 'price': order['avgPrice'], 'orderStatus': order['orderStatus'], 'qty': order['qty']}
        return {'status': False, 'retMsg': retMsg}

    def amend_order(self, orderId, takeProfit):
        params = {
            "orderId": orderId,
            "takeProfit": takeProfit,
            "tpslMode": "Partial",
            "tpOrderType": "Limit",
            "tpLimitPrice": takeProfit
        }
        resp = self._postOrder('/v5/order/amend', params)

    def set_trading_stop(self, symbol, tp, size, positionIdx):
        params = {
            "category": "linear",
            "symbol": symbol,
            "takeProfit": str(tp),
            # "stopLoss": "2000.1",
            "tpTriggerBy": "MarkPrice",
            # "slTriggerBy": "IndexPrice",
            "tpslMode": "Partial",
            "tpOrderType": "Limit",
            # "slOrderType": "Limit",
            "tpSize": str(size),
            "tpLimitPrice": str(tp),
            "positionIdx": positionIdx
        }
        resp = self._postOrder('/v5/position/trading-stop', params)

    def set_leverage(self, symbol, leverage):
        params = {"category": "linear",
                  "symbol": symbol,
                  "buyLeverage": str(leverage),
                  "sellLeverage": str(leverage)}
        resp = self._postOrder('/v5/position/set-leverage', params)
        return {'status': resp['retMsg'] == 'OK', 'retMsg': resp['retMsg']}

    def kline_price(self, symbol):
        params = {"category": "linear",
                  "symbol": symbol,
                  "interval": "1",
                  "limit": 1}
        resp = self._get('/v5/market/kline', params)
        if resp['retMsg'] == 'OK':
            return {'status': True, 'price': float(resp['result']['list'][0][4])}
        return {'status': False, 'retMsg': resp['retMsg']}

    def position_price(self, symbol, positionIdx):
        params = {
            "symbol": symbol,
            "category": "linear",
        }
        resp = self._get('/v5/position/list', params)
        for i in resp['result']['list']:
            if i['positionIdx'] == positionIdx:
                return float(i['avgPrice'])
        # return float(resp['result']['list'][positionIdx - 1]['avgPrice'])

    def cancel_order(self, symbol, orderId):
        params = {
            'category': "linear",
            "symbol": symbol,
            "orderId": orderId
        }

        resp = self._postOrder('/v5/order/cancel', params)
        print(resp)


# apikey = config.API_KEY
# secretkey = config.SECRET_KEY
# cl = Client(apikey, secretkey)
# print(cl.kline_price('BTCUSDT'))