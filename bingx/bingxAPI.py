from requests import get, post
from urllib.parse import urlencode

import requests
import time
import hmac
import hashlib

from config import *


class Client:
    SAPI = "https://open-api-vst.bingx.com"

    def __init__(self, apikey=None, secretkey=None):
        self.apikey = apikey
        self.secretkey = secretkey

    def get_server_time(self):
        url = self.SAPI + '/openApi/swap/v2/server/time'
        response = get(url)
        # print(response.json())
        return int(response.json()['data']['serverTime']) * 1000

    def genSignature(self, payload, timeStamp, apiKey, secretKey, recvWindow):
        param_str = str(timeStamp) + apiKey + recvWindow + payload
        hash = hmac.new(bytes(secretKey, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature
    
    def parseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "":
            return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return paramsStr + "timestamp=" + str(int(time.time() * 1000))
    
    def get_sign(self, payload):
        signature = hmac.new(self.secretkey.encode("utf-8"), payload.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()
        # print("sign=" + signature)
        return signature

    def send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (self.SAPI, path, urlpa, self.get_sign(urlpa))
        # print(url)
        headers = {
            'X-BX-APIKEY': self.apikey,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        return response

    def _postOrder(self, url, params):
        response = self.send_request(method='POST', path=url, urlpa=self.parseParam(params), payload='')
        return response.json()
    
    def _get(self, url, params):
        response = self.send_request(method='GET', path=url, urlpa=self.parseParam(params), payload='')
        return response.json()
    
    def _delete(self, url, params):
        response = self.send_request(method='DELETE', path=url, urlpa=self.parseParam(params), payload='')
        return response.json()
    # Not basic funcs

    def set_leverage(self, symbol, leverage):
        params = {
            "side": "LONG",
            "leverage": leverage,
            "symbol": symbol
        }
        # print(self._postOrder('/openApi/swap/v2/trade/leverage', params=params))
        params = {
            "side": "SHORT",
            "leverage": leverage,
            "symbol": symbol
        }
        # print(self._postOrder('/openApi/swap/v2/trade/leverage', params=params))

    def market_price(self, symbol):
        params = {
            "symbol": symbol,
        }

        resp = self._get('/openApi/swap/v1/ticker/price', params=params)
        return float(resp['data']['price'])
    
    def place_market_order(self, symbol, side, qty):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "positionSide": positionSide,
            "type": "MARKET"
        }
        response = self._postOrder('/openApi/swap/v2/trade/order', params=params)
        return response
    
    def place_limit_order(self, symbol, side, qty, price):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "positionSide": positionSide,
            "type": "LIMIT",
            "price": price
        }
        response = self._postOrder('/openApi/swap/v2/trade/order', params=params)['data']['order']
        return response
    
    def position_price(self, symbol, side):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
        }
        response = self._get('/openApi/swap/v2/user/positions', params=params)['data']
        for i in response:
            if i['positionSide'] == positionSide:
                return float(i['avgPrice'])
            
    def position_value(self, symbol, side):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
        }
        response = self._get('/openApi/swap/v2/user/positions', params=params)['data']
        for i in response:
            if i['positionSide'] == positionSide:
                return float(i['positionAmt'])
            
    def position_id(self, symbol, side):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
        }
        response = self._get('/openApi/swap/v2/user/positions', params=params)['data']
        for i in response:
            if i['positionSide'] == positionSide:
                return i['positionId']
            
    def cancel_order(self, symbol, orderId, side):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]        
        params = {
            "symbol": symbol,
            "orderId": orderId,
            "positionSide": positionSide
        }

        response = self._delete('/openApi/swap/v2/trade/order', params=params)

    def market_tp(self, symbol, side, price, qty):
        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        params = {
            "symbol": symbol,
            "type": "TAKE_PROFIT_MARKET",
            "side": side,
            "positionSide": positionSide,
            "stopPrice": price,
            "quantity": qty,
        }
        response = self._postOrder('/openApi/swap/v2/trade/order', params=params)['data']['order']
        return response

    def order_price(self, symbol, orderId):
        params = {"symbol": symbol,
                  "orderId": orderId}
        resp = self._get('/openApi/swap/v2/trade/order', params)['data']['order']
        return {'status': True, 'price': resp['price'], 'orderStatus': resp['status'], 'qty': resp['origQty']}

# cl = Client(apikey=APIKEY, secretkey=SECRETKEY)

# pos_v = cl.position_value('XRP-USDT', 'BUY')
# print(cl.market_tp('XRP-USDT', 'BUY', 0.6, pos_v))