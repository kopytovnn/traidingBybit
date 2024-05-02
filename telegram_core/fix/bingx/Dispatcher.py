import time
from fix.bingx.bingxAPI import Client
import asyncio
# from config import *
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
    
    def __init__(self, cl: Client, symbol: str, leverage: int, depo: float) -> None:
        # debug
        for i in self.step_map:
            self.step_map[i] = 0.1

        self.cl = cl
        self.symbol = symbol
        self.leverage = leverage
                # Change leverage in user account
        resp = cl.set_leverage(self.symbol, self.leverage)

        self.depo = depo / self.leverage  # User deposit in USDT
        self.price_history = {}  # History of order prices
        self.waiting_list = []  # Not opened limit orders

        self.step = 0

    def simple_market_buy(self, qty):
        return self.cl.place_market_order(symbol=self.symbol,
                                         side='BUY',
                                         qty=qty)

    def simple_market_sell(self, qty):
        return self.cl.place_market_order(symbol=self.symbol,
                                         side='SELL',
                                         qty=qty)

    def simple_limit_buy(self, qty, price):
        return self.cl.place_limit_order(symbol=self.symbol,
                                        side='BUY',
                                        qty=qty,
                                        price=price)

    def simple_limit_sell(self, qty, price):
        return self.cl.place_limit_order(symbol=self.symbol,
                                        side='SELL',
                                        qty=qty,
                                        price=price)
    
    async def long_queue_async(self):
        price = self.cl.market_price(self.symbol)
        long_step = 1
        base_depo = self.depo / price
        long_order = self.simple_market_buy(base_depo * self.value_map[1])
        print(f'Market Long order has opened: \t{long_order["data"]["order"]["orderId"]}')
        await asyncio.sleep(0)
        position_price = self.cl.position_price(self.symbol, 'BUY')
        price = position_price
        position_value = self.cl.position_value(self.symbol, 'BUY')
        tp = self.cl.market_tp(symbol=self.symbol,
                          side='BUY',
                          price=position_price * (1 + 0.1 / self.leverage),
                          qty=position_value)
        print(f'Take profit for Long order has created: \t{tp["orderId"]}', tp)

        
        long_qty = base_depo * self.value_map[long_step + 1]
        long_price = price * (1 - self.step_map[long_step + 1] / 100)
        averaging_long = self.simple_limit_buy(long_qty, long_price)
        print(f'Limit Long order has opened: \t{averaging_long["orderId"]}\n')


        while True:
            await asyncio.sleep(0)
            if long_step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 'BUY')
            if not position_price:
                print('Long position is null')
                self.cl.cancel_order(self.symbol, averaging_long['orderId'], 'BUY')
                return
            lo_info = self.cl.order_price(self.symbol, averaging_long['orderId'])
            long_status = lo_info['orderStatus']
            if long_status == 'FILLED':
                print('Long position have been filled')
                position_price = self.cl.position_price(self.symbol, 'BUY')
                position_value = self.cl.position_value(self.symbol, 'BUY')
                self.cl.cancel_order(symbol=self.symbol, orderId=tp['orderId'], side='BUY')
                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 + 0.1 / self.leverage),
                                  side='BUY',
                                  qty=position_value)
                print('Take profit for long position have been updated')                

                long_step += 1
                long_price = price * (1 - self.step_map[long_step + 1] / 100)
                long_qty = base_depo * self.value_map[long_step + 1]
                averaging_long = self.simple_limit_buy(long_qty, long_price)

    async def short_queue_async(self):
        price = self.cl.market_price(self.symbol)
        short_step = 1
        base_depo = self.depo / price
        short_order = self.simple_market_sell(base_depo * self.value_map[1])
        print(f'Market Short order has opened: \t{short_order["data"]["order"]["orderId"]}\n')
        await asyncio.sleep(0)
        position_price = self.cl.position_price(self.symbol, 'SELL')
        price = position_price
        position_value = self.cl.position_value(self.symbol, 'SELL')
        tp = self.cl.market_tp(symbol=self.symbol,
                          side='SELL',
                          price=position_price * (1 - 0.1 / self.leverage),
                          qty=position_value)
        print(f'Take profit for Short order has created: \t{tp["orderId"]}', tp)
        
        short_qty = base_depo * self.value_map[short_step + 1]
        short_price = price * (1 + self.step_map[short_step + 1] / 100)
        averaging_short = self.simple_limit_sell(short_qty, short_price)
        print(f'Limit Short order has opened: \t{averaging_short["orderId"]}\n')


        while True:
            await asyncio.sleep(0)
            if short_step == 8:
                return
            position_price = self.cl.position_price(self.symbol, 'SELL')
            if not position_price:
                print('Short position is Null')
                self.cl.cancel_order(self.symbol, averaging_short['orderId'], 'SELL')
                return
            so_info = self.cl.order_price(self.symbol, averaging_short['orderId'])
            short_status = so_info['orderStatus']
            if short_status == 'FILLED':
                print('Short order have been filled')
                position_price = self.cl.position_price(self.symbol, 'SELL')
                position_value = self.cl.position_value(self.symbol, 'SELL')
                self.cl.market_tp(symbol=self.symbol,
                                  price=position_price * (1 - 0.1 / self.leverage),
                                  side='SELL',
                                  qty=position_value)
                print('Take profit for short position have been updated')

                short_step += 1
                short_price = price * (1 - self.step_map[short_step + 1] / 100)
                short_qty = base_depo * self.value_map[short_step + 1]
                averaging_short = self.simple_limit_sell(short_qty, short_price)
                print(f'Short Limit Order have opened: \t{averaging_short["orderId"]}')

    async def long_loop(self):
        while True:
            await self.long_queue_async()

    async def short_loop(self):
        while True:
            await self.short_queue_async()

    async def upd(self):
        self.cl.set_leverage(self.symbol, 20)

        task1 = asyncio.create_task(self.long_loop())
        task2 = asyncio.create_task(self.short_loop())

        await task1
        await task2
