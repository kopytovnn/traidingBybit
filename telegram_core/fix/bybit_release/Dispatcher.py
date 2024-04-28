import time
from fix.bybit_release.bybitAPI import Client
from multiprocessing import Process
import asyncio
# import config


class Dispatcher:
    value_map = {1: 0.4,
                 2: 0.4,
                 3: 0.8,
                 4: 1.6,
                 5: 3.2,
                 6: 6.4,
                 7: 12.8,
                 8: 25.6}

    step_map = {1: 0,
                2: 0.3,
                3: 0.8,
                4: 1.8,
                5: 3.2,
                6: 6,
                7: 10,
                8: 15}

    circling_map = {
        "XRPUSDT": 0,
        "DOGEUSDT": 0,
        "BTCUSDT": 3,
        "ETHUSDT": 2,
        "ADAUSDT": 0,
        "LINKUSDT": 1,
        "XLMUSDT": 0,
        "DASHUSDT": 2,
        "NEOUSDT": 2,
        "TRXUSDT": 0,
        "EOSUSDT": 1,
        "LTCUSDT": 1,
        "APTUSDT": 2,
        "ATOMUSDT": 0
    }

    market_price = None

    def __init__(self, cl: Client, symbol: str, leverage: int, depo: float):
        # debug
        # for i in self.step_map:
        #     self.step_map[i] = self.step_map[i] / 50

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
            return value_coin
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

    async def long_queue_async(self, circling):
        price = self.cl.kline_price(self.symbol)['price']
        long_step = 1
        base_depo = self.depo / price
        long_order = self.simple_market_buy(round(base_depo * self.value_map[1], circling))
        await asyncio.sleep(0.1)

        position_price = self.cl.position_price(self.symbol, 1)
        price = position_price

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 + 0.1 / self.leverage),
                          positionIdx=1)

        long_qty = round(base_depo * self.value_map[long_step + 1], circling)
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)
        print(f'\tStart price: {price}, long limit price: {long_price} ~ {self.step_map[long_step + 1]}%')


        while True:
            await asyncio.sleep(0.1)

            position_price = self.cl.position_price(self.symbol, 1)
            # print('Long position:', position_price)
            if position_price == 0.0:
                print('long position is null')
                self.cl.cancel_order(self.symbol, averaging_long['orderId'])
                return
            if long_step == 7:
                continue
            lo_info = self.cl.order_price(averaging_long['orderId'])
            # price = self.cl.kline_price(self.symbol)['price']
            long_status = lo_info['orderStatus']
            if long_status == 'Filled':
                print('Long Limit Order has been filled')
                position_price = self.cl.position_price(self.symbol, 1)
                # self.cl.cancel_order(self.symbol, tp['orderId'])
                tp = self.cl.market_tp(symbol=self.symbol,
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
        await asyncio.sleep(0.1)

        position_price = self.cl.position_price(self.symbol, 2)
        price = position_price

        self.cl.market_tp(symbol=self.symbol,
                          price=position_price * (1 - 0.1 / self.leverage),
                          positionIdx=2)

        short_qty = round(base_depo * self.value_map[short_step + 1], circling)
        short_price = price * (1 + self.step_map[short_step + 1] / 100)
        averaging_short = self.simple_limit_sell(short_qty, short_price)

        while True:
            await asyncio.sleep(0.1)
            if short_step == 7:
                print('short step is equal 8')
                return
            position_price = self.cl.position_price(self.symbol, 2)
            if position_price == 0.0:
                print('short position is null')
                self.cl.cancel_order(self.symbol, averaging_short['orderId'])
                return

            so_info = self.cl.order_price(averaging_short['orderId'])
            # price = self.cl.kline_price(self.symbol)['price']
            short_status = so_info['orderStatus']
            if short_status == 'Filled':
                position_price = self.cl.position_price(self.symbol, 2)
                print('Short position:', position_price)
                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 - 0.1 / self.leverage),
                                  positionIdx=2)
                short_step += 1
                short_price = price * (1 + self.step_map[short_step + 1] / 100)
                short_qty = round(base_depo * self.value_map[short_step + 1], circling)
                averaging_short = self.simple_limit_sell(short_qty, short_price)

    async def long_loop(self, circling):
        while True:
            print("long_loop start")
            await self.long_queue_async(circling)
            print("long_loop end")

    async def short_loop(self, circling):
        while True:
            print("short_loop start")
            await self.short_queue_async(circling)
            print("short_loop end")

    async def upd_v6(self):
        self.cl.switch_position_mode(self.symbol, 3)
        circling = self.circling_map[self.symbol]

        task1 = asyncio.create_task(self.long_loop(circling))
        task2 = asyncio.create_task(self.short_loop(circling))

        await task1
        await task2
