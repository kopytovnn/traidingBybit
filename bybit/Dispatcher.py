import time
from bybitAPI import Client
import config


class Dispatcher:
    value_map = {1: 0.2,
                 2: 0.2,
                 3: 0.4,
                 4: 0.8,
                 5: 1.6,
                 6: 3.2,
                 7: 6.4,
                 8: 12.8}

    step_map = {1: 0,
                2: 0.3,
                3: 0.8,
                4: 1.8,
                5: 3.2,
                6: 6,
                7: 10,
                8: 15}

    market_price = None

    def __init__(self, cl: Client, symbol: str, leverage: int, depo: float):
        # debug
        for i in self.step_map:
            self.step_map[i] = self.step_map[i] / 50

        # Imported settings
        self.cl = cl
        self.symbol = symbol
        self.leverage = leverage
        # Change leverage in user account
        resp = cl.set_leverage(self.symbol, self.leverage)
        if resp['status']:
            print(f'Leverage successfully changed')
        else:
            print(resp['retMsg'])
        # self.cl.switch_position_mode(self.symbol)
        #
        self.depo = depo  # User deposit in USDT
        self.price_history = {}  # History of order prices
        self.waiting_list = []  # Not opened limit orders

        self.step = 0

    def form_qty(self, percents):
        value_usdt = self.depo * percents * 0.01
        if self.market_price['status']:
            value_coin = value_usdt / self.market_price['price']
            return round(value_coin, 1)
        return

    def triumvirate(self, side):
        if side == 'Buy':
            averaging_value = self.value_map[self.step + 1]  # averaging
            averaging_price = self.market_price['price'] * (1 - self.step_map[self.step + 2] / 100)
            tp_price = self.market_price['price'] * 1.1
            tp_price = self.market_price['price'] * (1 + 0.1 / self.leverage)
        else:
            averaging_value = self.value_map[self.step + 1]
            averaging_price = self.market_price['price'] * (1 + self.step_map[self.step + 2] / 100)
            tp_price = self.market_price['price'] * (1 - 0.1 / self.leverage)

        order1 = self.cl.market_open_order(symbol=self.symbol,
                                           qty=self.form_qty(self.value_map[self.step + 1]),
                                           side=side,
                                           takeProfit=round(tp_price, 1))
        print(order1)
        averaging = self.cl.limit_open_order(symbol=self.symbol,
                                             side=side,
                                             price=round(averaging_price, 1),
                                             qty=round(averaging_value, 1))
        self.waiting_list.append(averaging)

    def upd_v2(self):
        self.cl.switch_position_mode(self.symbol, 3)
        price = self.cl.kline_price(self.symbol)['price']
        long_order = self.cl.market_open_order(symbol=self.symbol,
                                               side='Buy',
                                               qty=self.depo * self.value_map[0 + 1] / 100,
                                               takeProfit=round(price * 1.01, 1))
        short_order = self.cl.market_open_order(symbol=self.symbol,
                                                side='Sell',
                                                qty=self.depo * self.value_map[0 + 1] / 100,
                                                takeProfit=round(price * 0.99, 1))
        new_price = self.cl.kline_price(self.symbol)['price']
        while abs(1 - new_price / price) < self.step_map[2] / 100:
            new_price = self.cl.kline_price(self.symbol)['price']
        if new_price < price:
            side = 'Buy'
            mp = -1
        else:
            side = 'Sell'
            mp = 1
        for i in range(1, len(self.value_map)):
            new_price *= 1 + mp * self.step_map[i] / 100
            qty = self.depo * self.value_map[i + 1] / 100
            order = self.cl.limit_open_order(symbol=self.symbol,
                                             side=side,
                                             price=round(new_price, 1),
                                             qty=qty,
                                             takeProfit=round(new_price * (1 - mp * 0.1 / self.leverage), 3))
            print(order)

    def upd(self):
        self.market_price = self.cl.kline_price(self.symbol)

        if self.step == 0:
            self.triumvirate('Buy')
            self.triumvirate('Sell')
            self.step += 1
            self.price_history[0] = self.market_price['price']
        else:
            for i in self.waiting_list:
                limit_orderId = i['orderId']
                price = self.cl.order_price(limit_orderId)
                if not price['status']:
                    print(f'\tLimit order {limit_orderId} not opened yet')
                else:
                    self.waiting_list.remove(i)
                    if price['orderStatus'] in ['PartiallyFilled', 'Filled']:
                        self.step += 1
                        if price['price'] > self.market_price['price']:
                            averaging = self.cl.limit_open_order(symbol=self.symbol,
                                                                 side='Sell',
                                                                 price=round(self.market_price['price'] *
                                                                             (1 + self.step_map[self.step + 2] / 100),
                                                                             1),
                                                                 qty=round(self.value_map[self.step + 1], 1))
                        else:
                            averaging = self.cl.limit_open_order(symbol=self.symbol,
                                                                 side='Buy',
                                                                 price=round(self.market_price['price'] *
                                                                             (1 - self.step_map[self.step + 2] / 100),
                                                                             1),
                                                                 qty=round(self.value_map[self.step + 1], 1))
                        self.waiting_list.append(averaging)
                        self.step += 1
                    else:
                        print(price, limit_orderId)

    def simple_market_buy(self, qty):
        return self.cl.market_open_order(symbol=self.symbol,
                                         side='Buy',
                                         qty=qty)

    def simple_market_sell(self, qty):
        return self.cl.market_open_order(symbol=self.symbol,
                                         side='Sell',
                                         qty=qty)

    def simple_limit_buy(self, qty, price):
        return self.cl.limit_open_order(symbol=self.symbol,
                                        side='Buy',
                                        qty=qty,
                                        price=price)

    def simple_limit_sell(self, qty, price):
        return self.cl.limit_open_order(symbol=self.symbol,
                                        side='Sell',
                                        qty=qty,
                                        price=price)

    def upd_v3(self):
        self.cl.switch_position_mode(self.symbol, 3)
        price = self.cl.kline_price(self.symbol)['price']
        all_orders = {'Long': None, 'Short': None}
        limit_orders = {'Long': [], 'Short': []}
        long_order = self.simple_market_buy(0.01)
        short_order = self.simple_market_sell(0.01)

        averaging_long = self.simple_limit_buy(0.01, price * 0.999)
        averaging_short = self.simple_limit_sell(0.01, price * 1.001)
        limit_orders['Short'] = averaging_short
        limit_orders['Long'] = averaging_long
        while True:
            short_status = self.cl.order_price(averaging_short['orderId'])['orderStatus']
            long_status = self.cl.order_price(averaging_long['orderId'])['orderStatus']
            print(short_status)
            print(long_status)
            if short_status == 'Filled':
                averaging_short = self.simple_limit_sell(0.01, price * 1.01)
                print(averaging_short)
            if long_status == 'Filled':
                averaging_long = self.simple_limit_buy(0.01, price * 0.99)
                print(averaging_long)

    def upd_v4(self):
        self.cl.switch_position_mode(self.symbol, 3)
        price = self.cl.kline_price(self.symbol)['price']
        circling = 2
        long_step = 1
        short_step = 1
        lt_price, lt_qty = 0, 0
        st_price, st_qty = 0, 0
        base_depo = self.depo / price

        long_order = self.simple_market_buy(round(base_depo * self.value_map[1], circling))
        lo_info = self.cl.order_price(long_order['orderId'])
        lt_qty += float(lo_info['qty'])
        lt_price += float(lo_info['qty']) * float(lo_info['price'])
        short_order = self.simple_market_sell(round(base_depo * self.value_map[1], circling))
        so_info = self.cl.order_price(short_order['orderId'])
        st_qty += float(so_info['qty'])
        st_price += float(so_info['qty']) * float(so_info['price'])

        self.cl.set_trading_stop(symbol=self.symbol,
                                 tp=lt_price / lt_qty * (1 + 0.1 / self.leverage),
                                 size=lt_qty,
                                 positionIdx=1)
        self.cl.set_trading_stop(symbol=self.symbol,
                                 tp=st_price / st_qty * (1 - 0.1 / self.leverage),
                                 size=st_qty,
                                 positionIdx=2)

        short_qty = round(base_depo * self.value_map[long_step + 1], circling)
        long_qty = round(base_depo * self.value_map[short_step + 1], circling)
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        short_price = price * (1 + self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)
        averaging_short = self.simple_limit_sell(short_qty, short_price)

        while True:
            so_info = self.cl.order_price(averaging_short['orderId'])
            short_status = so_info['orderStatus']
            lo_info = self.cl.order_price(averaging_long['orderId'])
            long_status = lo_info['orderStatus']
            if short_status == 'Filled':
                short_step += 1
                st_qty += float(so_info['qty'])
                st_price += float(so_info['qty']) * float(so_info['price'])
                self.cl.set_trading_stop(symbol=self.symbol,
                                         tp=st_price / st_qty * (1 - 0.1 / self.leverage),
                                         size=st_qty,
                                         positionIdx=2)

                short_price = price * (1 + self.step_map[short_step + 1] / 100)
                short_qty = round(base_depo * self.value_map[short_step + 1], circling)
                averaging_short = self.simple_limit_sell(short_qty, short_price)
            if long_status == 'Filled':
                long_step += 1
                lt_qty += float(lo_info['qty'])
                lt_price += float(lo_info['qty']) * float(lo_info['price'])
                self.cl.set_trading_stop(symbol=self.symbol,
                                         tp=lt_price / lt_qty * (1 + 0.1 / self.leverage),
                                         size=lt_qty,
                                         positionIdx=1)

                long_price = price * (1 - self.step_map[long_step + 1] / 100)
                long_qty = round(base_depo * self.value_map[long_step + 1], circling)
                averaging_long = self.simple_limit_buy(long_qty, long_price)

    def long_queue(self, circling):
        price = self.cl.kline_price(self.symbol)['price']
        long_step = 1
        base_depo = self.depo / price

        long_qty = round(base_depo * self.value_map[long_step + 1], circling)
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)

        while True:
            lo_info = self.cl.order_price(averaging_long['orderId'])
            long_status = lo_info['orderStatus']
            if long_status == 'Filled':
                long_step += 1
                long_price = price * (1 - self.step_map[long_step + 1] / 100)
                long_qty = round(base_depo * self.value_map[long_step + 1], circling)
                averaging_long = self.simple_limit_buy(long_qty, long_price)

    def upd_v5(self):
        self.cl.switch_position_mode(self.symbol, 3)
        circling = 2
        self.long_queue(circling)


if __name__ == '__main__':
    apikey = config.API_KEY
    secretkey = config.SECRET_KEY
    cl = Client(apikey, secretkey)

    symbol = 'ETHUSDT'
    leverage = 20
    depo = 10000.0

    dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=depo)
    dp.upd_v5()
