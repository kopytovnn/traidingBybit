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

    def update(self):
        try:
            self.get_balance()
            self.apiStatus = True
            
            for i in coins:
                self.get_positions(i + 'USDT')
            
            for i in coins:
                self.get_limits(i + 'USDT')
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


    