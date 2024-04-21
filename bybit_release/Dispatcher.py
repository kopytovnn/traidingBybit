import time
from bybit_release.bybitAPI import Client
from multiprocessing import Process
import asyncio
# import config


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
        # for i in self.step_map:
        #     self.step_map[i] = self.step_map[i] / 10

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

        self.depo = depo / self.leverage  # User deposit in USDT
        self.price_history = {}  # History of order prices
        self.waiting_list = []  # Not opened limit orders

        self.step = 0

    def form_qty(self, percents):
        value_usdt = self.depo * percents * 0.01
        if self.market_price['status']:
            value_coin = value_usdt / self.market_price['price']
            return round(value_coin, 1)
        return

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
        long_order = self.simple_market_buy(round(base_depo * self.value_map[1], circling))

        position_price = self.cl.position_price(self.symbol, 1)

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 + 0.1 / self.leverage),
                          positionIdx=1)

        long_qty = round(base_depo * self.value_map[long_step + 1], circling)
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)

        while True:
            if self.step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 1)
            if position_price == 0.0:
                self.cl.cancel_order(self.symbol, averaging_long['orderId'])
                return

            lo_info = self.cl.order_price(averaging_long['orderId'])
            price = self.cl.kline_price(self.symbol)['price']
            long_status = lo_info['orderStatus']
            if long_status == 'Filled':
                position_price = self.cl.position_price(self.symbol, 1)

                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 + 0.1 / self.leverage),
                                  positionIdx=1)

                long_step += 1
                long_price = price * (1 - self.step_map[long_step + 1] / 100)
                long_qty = round(base_depo * self.value_map[long_step + 1], circling)
                averaging_long = self.simple_limit_buy(long_qty, long_price)

    def short_queue(self, circling):
        price = self.cl.kline_price(self.symbol)['price']
        short_step = 1
        base_depo = self.depo / price
        short_order = self.simple_market_sell(round(base_depo * self.value_map[1], circling))

        position_price = self.cl.position_price(self.symbol, 2)
        print(position_price)

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 - 0.1 / self.leverage),
                          positionIdx=2)

        short_qty = round(base_depo * self.value_map[short_step + 1], circling)
        short_price = price * (1 + self.step_map[short_step + 1] / 100)
        averaging_short = self.simple_limit_sell(short_qty, short_price)

        while True:
            if self.step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 2)
            if position_price == 0.0:
                self.cl.cancel_order(self.symbol, averaging_short['orderId'])
                return

            so_info = self.cl.order_price(averaging_short['orderId'])
            price = self.cl.kline_price(self.symbol)['price']
            short_status = so_info['orderStatus']
            if short_status == 'Filled':
                position_price = self.cl.position_price(self.symbol, 1)
                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 - 0.1 / self.leverage),
                                  positionIdx=2)
                short_step += 1
                short_price = price * (1 + self.step_map[short_step + 1] / 100)
                short_qty = round(base_depo * self.value_map[short_step + 1], circling)
                averaging_short = self.simple_limit_sell(short_qty, short_price)

    def a(self, circling):
        while True:
            self.long_queue(circling)

    def b(self, circling):
        while True:
            self.short_queue(circling)

    def upd_v5(self):
        self.cl.switch_position_mode(self.symbol, 3)
        circling = 2

        # self.b(circling)

        p1 = Process(target=self.a, args=(circling,), daemon=True)
        p2 = Process(target=self.b, args=(circling,), daemon=True)
        p1.start()
        p2.start()
        # p1.join()
        # p2.join()

    async def long_queue_async(self, circling):
        price = self.cl.kline_price(self.symbol)['price']
        long_step = 1
        base_depo = self.depo / price
        long_order = self.simple_market_buy(round(base_depo * self.value_map[1], circling))
        await asyncio.sleep(1)

        position_price = self.cl.position_price(self.symbol, 1)

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 + 0.1 / self.leverage),
                          positionIdx=1)

        long_qty = round(base_depo * self.value_map[long_step + 1], circling)
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)

        while True:
            await asyncio.sleep(1)

            if self.step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 1)
            if position_price == 0.0:
                self.cl.cancel_order(self.symbol, averaging_long['orderId'])
                return

            lo_info = self.cl.order_price(averaging_long['orderId'])
            price = self.cl.kline_price(self.symbol)['price']
            long_status = lo_info['orderStatus']
            if long_status == 'Filled':
                position_price = self.cl.position_price(self.symbol, 1)

                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 + 0.1 / self.leverage),
                                  positionIdx=1)

                long_step += 1
                long_price = price * (1 - self.step_map[long_step + 1] / 100)
                long_qty = round(base_depo * self.value_map[long_step + 1], circling)
                averaging_long = self.simple_limit_buy(long_qty, long_price)

    async def short_queue_async(self, circling):
        price = self.cl.kline_price(self.symbol)['price']
        short_step = 1
        base_depo = self.depo / price
        short_order = self.simple_market_sell(round(base_depo * self.value_map[1], circling))
        await asyncio.sleep(1)

        position_price = self.cl.position_price(self.symbol, 2)
        print(position_price)

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 - 0.1 / self.leverage),
                          positionIdx=2)

        short_qty = round(base_depo * self.value_map[short_step + 1], circling)
        short_price = price * (1 + self.step_map[short_step + 1] / 100)
        averaging_short = self.simple_limit_sell(short_qty, short_price)

        while True:
            await asyncio.sleep(1)
            if self.step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 2)
            if position_price == 0.0:
                self.cl.cancel_order(self.symbol, averaging_short['orderId'])
                return

            so_info = self.cl.order_price(averaging_short['orderId'])
            price = self.cl.kline_price(self.symbol)['price']
            short_status = so_info['orderStatus']
            if short_status == 'Filled':
                position_price = self.cl.position_price(self.symbol, 1)
                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 - 0.1 / self.leverage),
                                  positionIdx=2)
                short_step += 1
                short_price = price * (1 + self.step_map[short_step + 1] / 100)
                short_qty = round(base_depo * self.value_map[short_step + 1], circling)
                averaging_short = self.simple_limit_sell(short_qty, short_price)

    async def long_loop(self, circling):
        while True:
            await self.long_queue_async(circling)

    async def short_loop(self, circling):
        while True:
            await self.short_queue_async(circling)

    async def upd_v6(self):
        self.cl.switch_position_mode(self.symbol, 3)
        circling = 2

        task1 = asyncio.create_task(self.long_queue_async(circling))
        task2 = asyncio.create_task(self.short_queue_async(circling))

        await task1
        await task2


# if __name__ == '__main__':
#     async def main():
#         apikey = config.API_KEY
#         secretkey = config.SECRET_KEY
#         cl = Client(apikey, secretkey)
#
#         symbol = 'ETHUSDT'
#         leverage = 20
#         depo = 10000.0
#
#         dp = Dispatcher(cl=cl, symbol=symbol, leverage=leverage, depo=depo)
#         await dp.upd_v6()
#
#     asyncio.run(main())
