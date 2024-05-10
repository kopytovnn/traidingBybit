from fix.Bybit.bybitAPI import Client
from fix.Bybit.Order import *
from fix.Bybit.Position import *

import asyncio


class Dispatcher:
    valueMap = {1: 0.4,
                 2: 0.4,
                 3: 0.8,
                 4: 1.6,
                 5: 3.2,
                 6: 6.4,
                 7: 12.8,
                 8: 25.6}

    stepMap = {1: 0,
                2: 0.3,
                3: 0.8,
                4: 1.8,
                5: 3.2,
                6: 6,
                7: 10,
                8: 15}

    def __init__(self, cl: Client, symbol: str, leverage: int, depo: float) -> None:
        self.cl = cl
        self.symbol = symbol
        self.leverage = leverage
        self.cl.set_leverage(self.symbol, self.leverage)
        self.depo = depo / (100 / self.leverage)

        # test
        # for i in self.stepMap:
        #     self.stepMap[i] = self.stepMap[i] / 10

    def tokenPrice(self) -> float:
        return self.cl.kline_price(self.symbol)['price']

    async def shortAlgo(self):
        startPrice = self.tokenPrice()
        step = 1
        baseDepo = self.depo / startPrice

        qty = baseDepo * self.valueMap[1]
        marketOrder = ShortMarketOrder(self.cl, self.symbol)
        marketOrder.open(qty)

        position = ShortPosition(self.cl, self.symbol, self.leverage)
        position.Update()
        position.takeProfit()

        limitQty = baseDepo * self.valueMap[step + 1]
        limitPrice = marketOrder.price * (1 + self.stepMap[step + 1] / 100)
        limitOrder = ShortLimitOrder(self.cl, self.symbol)
        limitOrder.open(position.qty / position.price, limitPrice)
        await asyncio.sleep(1)

        while True:
            limitOrder.Update()
            position.Update()
            if position.price == 0:
                limitOrder.findncancel()
                return
            if step == 7:
                position.takeProfit80()
                continue
            if limitOrder.status == 'Filled':
                position.takeProfit()
                limitOrder.findncancel()
                step += 1

                limitQty = baseDepo * self.valueMap[step + 1]
                limitPrice = marketOrder.price * (1 + self.stepMap[step + 1] / 100)
                limitOrder = ShortLimitOrder(self.cl, self.symbol)
                limitOrder.open(position.qty / position.price, limitPrice)
                limitOrder.Update()
            await asyncio.sleep(1)


    async def longAlgo(self):
        startPrice = self.tokenPrice()
        step = 1
        baseDepo = self.depo / startPrice

        qty = baseDepo * self.valueMap[1]
        marketOrder = LongMarketOrder(self.cl, self.symbol)
        marketOrder.open(qty)

        position = LongPosition(self.cl, self.symbol, self.leverage)
        position.Update()
        position.takeProfit()

        limitQty = baseDepo * self.valueMap[step + 1]
        limitPrice = marketOrder.price * (1 - self.stepMap[step + 1] / 100)
        limitOrder = LongLimitOrder(self.cl, self.symbol)
        limitOrder.open(position.qty / position.price, limitPrice)

        await asyncio.sleep(1)
        while True:
            limitOrder.Update()
            position.Update()
            if position.price == 0:
                limitOrder.findncancel()
                return
            if step == 7:
                position.takeProfit80()
                continue
            if limitOrder.status == 'Filled':
                position.takeProfit()
                limitOrder.findncancel()
                step += 1

                limitQty = baseDepo * self.valueMap[step + 1]
                limitPrice = marketOrder.price * (1 - self.stepMap[step + 1] / 100)
                limitOrder = LongLimitOrder(self.cl, self.symbol)
                limitOrder.open(position.qty / position.price, limitPrice)
                limitOrder.Update()
            await asyncio.sleep(1)

    async def shortLoop(self):
        while True:
            # try:
            #     await self.shortAlgo()
            # except BaseException:
            #     continue
            await self.shortAlgo()

    async def longLoop(self):
        # while True:
        #     try:
        #         await self.longAlgo()
        #     except BaseException:
        #         continue
        while True:
            await self.longAlgo()


    def geventEngineStart(self):
        import gevent

        gevent.joinall([
            gevent.spawn(self.shortLoop),
            gevent.spawn(self.longAlgo)
        ])

    async def asyncEngineStart(self):
        self.cl.switch_position_mode(self.symbol, 3)

        task1 = asyncio.create_task(self.longLoop())
        task2 = asyncio.create_task(self.shortLoop())

        await task1
        await task2

