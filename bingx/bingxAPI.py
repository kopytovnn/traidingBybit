from requests import get, post
from urllib.parse import urlencode

import requests
import time
import hmac
from hashlib import sha256

import config


class Client:
    APIURL = "https://open-api-vst.bingx.com"

    def __init__(self, apikey=None, secretkey=None):
        self.apikey = apikey
        self.secretkey = secretkey

    def get_sign(self, payload):
        signature = hmac.new(self.secretkey.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        # print("sign=" + signature)
        return signature

    def send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (self.APIURL, path, urlpa, self.get_sign(urlpa))
        # print(url)
        headers = {
            'X-BX-APIKEY': self.apikey,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        try:
            return response.json()
        except BaseException:
            print('\t\tError')
            print(response.text)
            return None

    def parseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        if paramsStr != "":
            return paramsStr + "&timestamp=" + str(int(time.time() * 1000))
        else:
            return paramsStr + "timestamp=" + str(int(time.time() * 1000))

    # IMPORTANT:
    def place_order(self, symbol, side='SELL', quantity=0.1, stopPrices=None):
        payload = {}
        path = '/openApi/swap/v2/trade/order'
        method = "POST"

        positionSide = {"BUY": "LONG", "SELL": "SHORT"}[side]
        if side == "SELL":
            stopLoss, takeProfit = max(stopPrices), min(stopPrices)
        else:
            stopLoss, takeProfit = min(stopPrices), max(stopPrices)
        print(quantity)
        paramsMap = {
            "recvWindow": "10000",
            "symbol": symbol,
            "side": side,
            "positionSide": positionSide,
            "type": "MARKET",
            "quantity": quantity,
            "takeProfit": "{\"type\": \"TAKE_PROFIT_MARKET\", \"stopPrice\": " + str(takeProfit) + "}",
            # "stopLoss": "{\"type\": \"STOP_MARKET\", \"stopPrice\": " + str(stopLoss) + "}"
        }
        paramsStr = self.parseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def bulk_orders_bs(self, symbol, quantity=0.1):
        payload = {}
        path = '/openApi/swap/v2/trade/batchOrders'
        method = "POST"
        paramsMap = {
            "batchOrders": "[{\"symbol\": \""
                           + symbol +
                           "\",\"type\": \"MARKET\",\"side\": \"BUY\",\"positionSide\": \"LONG\",\"quantity\": "
                           + str(quantity) + "},"
                                             "{\"symbol\": \" "
                           + symbol +
                           "\",\"type\": \"MARKET\",\"side\": \"SELL\",\"positionSide\": \"SHORT\",\"quantity\": "
                           + str(quantity) + "}]"
        }
        paramsStr = self.parseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def last_price(self, symbol):
        payload = {}
        path = '/openApi/swap/v1/market/markPriceKlines'
        method = "GET"
        paramsMap = {
            "symbol": symbol,
            "interval": "4h",
            "limit": "10",
            "startTime": int(time.time() * 1000)
        }
        paramsStr = self.parseParam(paramsMap)
        response = self.send_request(method, path, paramsStr, payload)
        try:
            close_price = float(response["data"][0]["close"])
            # print('last_price:\t', close_price)
            return close_price
        except BaseException:
            return None

    def set_leverage(self, symbol, side, leverage):
        payload = {}
        path = '/openApi/swap/v2/trade/leverage'
        method = "POST"
        paramsMap = {
            "leverage": str(leverage),
            "side": side,
            "symbol": symbol,
            "timestamp": int(time.time() * 1000)
        }
        paramsStr = self.parseParam(paramsMap)
        return self.send_request(method, path, paramsStr, payload)

    def user_balance(self):
        payload = {}
        path = '/openApi/swap/v2/user/balance'
        method = "GET"
        paramsMap = {
            "timestamp": int(time.time() * 1000)
        }
        paramsStr = self.parseParam(paramsMap)
        response = self.send_request(method, path, paramsStr, payload)
        # print(response)
        print(response)
        return float(response["data"]["balance"]["balance"])
