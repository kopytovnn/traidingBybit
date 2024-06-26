from fix.Bybit.bybitAPI import Client


class Position:
    positionIdxMap = {'Buy': 1, 'Sell': 2}

    def __init__(self, cl: Client, symbol: str, side: str, leverage: int) -> None:
        self.cl = cl
        self.symbol = symbol
        self.side = side
        self.leverage = leverage
        self.price = None
        self.qty = None
        self.tp = None

    def Update(self):
        positionIdx = self.positionIdxMap[self.side]
        resp = self.cl.position_price(symbol=self.symbol,
                                      positionIdx=positionIdx)
        # print(resp)
        for position in resp:
            # print('\t', position, positionIdx)
            if position['positionIdx'] == positionIdx:
                self.price = float(position['avgPrice'])
                self.tp = position['takeProfit']
                try:
                    self.qty = float(position['positionValue'])
                except ValueError:
                    self.qty = 0

    def takeProfit(self, price, side):
        print(f'takeProfit: {price}, Position price: {self.price}')
        positionIdx = self.positionIdxMap[side]
        resp = self.cl.market_tp(symbol=self.symbol,
                                 price=price,
                                 positionIdx=positionIdx)
        self.tp = price

    def __repr__(self) -> str:
        return f'Position type: {type(self)}, price: {self.price}'


class ShortPosition(Position):
    def __init__(self, cl: Client, symbol: str, leverage: int) -> None:
        super().__init__(cl, symbol, 'Sell', leverage)

    def Update(self):
        return super().Update()
    
    def takeProfit(self):
        super().Update()
        price = self.price * (1 - 0.1 / self.leverage)
        try:
            return super().takeProfit(price, 'Sell')
        except:
            if self.cl.kline_price(self.symbol)['price'] < self.price:
                print(f'''self.cl.kline_price(self.symbol)['price'] = {self.cl.kline_price(self.symbol)['price']}
                    self.price = {self.price}
                    Short''')
                
                return self.cl.market_close_short(self.symbol, str(self.qty / self.price))
    
    def takeProfit80(self):
        super().Update()
        price = self.price * (1 - 0.8 / self.leverage)
        return super().takeProfit(price, 'Sell')
    

class LongPosition(Position):
    def __init__(self, cl: Client, symbol: str, leverage: int) -> None:
        super().__init__(cl, symbol, 'Buy', leverage)

    def Update(self):
        return super().Update()
    
    def takeProfit(self):
        super().Update()
        price = self.price * (1 + 0.1 / self.leverage)
        try:
            return super().takeProfit(price, 'Buy')
        except:
            if self.cl.kline_price(self.symbol)['price'] > self.price:
                print(f'''self.cl.kline_price(self.symbol)['price'] = {self.cl.kline_price(self.symbol)['price']}
                    self.price = {self.price}
                    Long''')
                return self.cl.market_close_long(self.symbol, str(self.qty / self.price))
            
    
    def takeProfit80(self):
        super().Update()
        price = self.price * (1 + 0.8 / self.leverage)
        return super().takeProfit(price, 'Buy')