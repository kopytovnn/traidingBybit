from fix.Bybit.bybitAPI import *


coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']


class SmallPosition():
    symbol = ''
    positions = 0
    orders = 0
    tps = 0

    def __repr__(self) -> str:
        return f'{self.symbol}: Позиций: {self.positions}, Ордеров: {self.orders}, ТП: {self.tps}'


class SmallBybit():
    def __init__(self, apikey, secretkey) -> None:
        self.apikey = apikey
        self.secretkey = secretkey
        self.pairs = {}  # symbol: SmallPosition
        self.cl = Client(apikey, secretkey)


        self.coinControl = {}

        self.balance = 0
        self.apiStatus = None

    def get_balance(self):
        response = self.cl.get_balance()
        print()
        self.balance = float(response['result']['list'][0]['totalEquity'])

    def get_positions(self, symbol):
        response = self.cl.position_price(symbol, 1)
        sp = SmallPosition()
        sp.symbol = symbol
        for pos in response:
            if pos['avgPrice'] and pos['avgPrice'] != '0':
                sp.positions += 1
            if pos['takeProfit']:
                sp.tps += 1
        self.coinControl[symbol] = sp

    def get_limits(self, symbol):
        response = self.cl.all_orders(symbol)
        if response:
            self.coinControl[symbol].orders = len(response) - self.coinControl[symbol].tps

    def endnclose(self, symbol):
        response = self.cl.close_pos(symbol)
        print(response)
        response = self.cl.cancel_all_limit_orders(symbol, 'Buy')
        print(response)
        response = self.cl.cancel_all_limit_orders(symbol, 'Sell')
        print(response)

    def update(self, a):
        # return 0
        try:
            self.get_balance()
            self.apiStatus = True
            
            self.get_positions(a.symbol + 'USDT')
            
            self.get_limits(a.symbol + 'USDT')
            print(self.coinControl)
        except BaseException:
            self.apiStatus = False
            print('Api неверные')

    def monitoring(self):
        answer = ""
        for i in self.coinControl:
            if "Позиций: 0" not in str(self.coinControl[i]):
                answer += str(self.coinControl[i]) + '\n'
        return answer
    

    def statistics(self, symbol):
        response = self.cl.get_closed_PnL(symbol)

        import pandas as pd
        pd.DataFrame(response['result']['list']).to_csv('out.csv', index=False)


        print(response)

    