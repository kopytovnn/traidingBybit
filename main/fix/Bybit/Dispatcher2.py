from fix.Bybit.bybitAPI import Client
from fix.Bybit.Order import *
from fix.Bybit.Position import *

import asyncio


class Dispatcher:
    valueMap = {1: 0.2,
                 2: 0.2,
                 3: 0.4,
                 4: 0.8,
                 5: 1.6,
                 6: 3.2,
                 7: 6.4,
                 8: 12.8}

    stepMap = {1: 0,
                2: 0.3,
                3: 0.8,
                4: 1.8,
                5: 3.2,
                6: 6,
                7: 10,
                8: 15}

    def __init__(self, cl: Client, symbol: str, leverage: int, depo: float, uid=None) -> None:
        self.cl = cl
        self.symbol = symbol
        self.leverage = leverage
        self.cl.set_leverage(self.symbol, self.leverage)
        self.depo = depo / (100 / self.leverage)
        self.uid = uid

        # test
        # for i in self.stepMap:
        #     self.stepMap[i] = self.stepMap[2] / 100

    def tokenPrice(self) -> float:
        return self.cl.kline_price(self.symbol)['price']

    async def shortAlgo(self):
        startPrice = self.tokenPrice()
        step = 1
        baseDepo = self.depo / startPrice

        position = ShortPosition(self.cl, self.symbol, self.leverage)
        position.Update()
        if position.price != 0:
            print('Short pos exists!')
            position.takeProfit()
            print('Short tp corrected')
            limitOrder = ShortLimitOrder(self.cl, self.symbol)
            limitOrder.findncancel()
            print('Short limit orders have been canceled')
            start_qty = baseDepo * self.valueMap[1]
            
            # print(start_qty, position.qty)
            print(start_qty, position.price, startPrice, position.qty, 
                  start_qty * startPrice, start_qty * position.price)
            startValueUsdt = start_qty * startPrice
            ratio = position.qty / startValueUsdt
            from math import log
            step = round(log(ratio, 2), 0) + 1

            marketOrder = ShortMarketOrder(self.cl, self.symbol)
            marketOrder.price = position.price
            print('Short step', step)
        else:
            qty = baseDepo * self.valueMap[1]
            marketOrder = ShortMarketOrder(self.cl, self.symbol)
            marketOrder.open(qty)
            print(marketOrder)

            position = ShortPosition(self.cl, self.symbol, self.leverage)
            position.Update()
            position.takeProfit()
            print(position)
            
        limitQty = baseDepo * self.valueMap[step + 1]
        print(step + 1)

        limitPrice = marketOrder.price * (1 + self.stepMap[step + 1] / 100)
        limitOrder = ShortLimitOrder(self.cl, self.symbol)
        limitOrder.open(position.qty / limitPrice, limitPrice)
        print(limitOrder)
        await asyncio.sleep(1)

        while True:
            # print('Short', step)
            limitOrder.Update()
            position.Update()
            if position.price == 0:
                print('\n', position, '\n', limitOrder)
                limitOrder.findncancel()
                print('\n', position, '\n', limitOrder)
                print('short pos is null')
                return
            if not position.tp:
                position.takeProfit()
                self.tprecoveryMSG()
            if limitOrder.status == 'Cancelled' and step < 7:
                print('\n', position, '\n', limitOrder, 'short limit irder filled')
                self.limitrecoveryMSG()

                limitPrice = limitOrder.price
                limitQty = limitOrder.qty
                limitOrder = ShortLimitOrder(self.cl, self.symbol)
                limitOrder.open(limitQty, limitPrice)
                limitOrder.Update()
                print('\n', position, '\n', limitOrder)

            if limitOrder.status == 'Filled' and step < 7:
                print('\n', position, '\n', limitOrder, 'short limit irder filled')
                position.Update()
                position.takeProfit()
                limitOrder.findncancel()
                step += 1

                limitQty = baseDepo * self.valueMap[step + 1]
                limitPrice = marketOrder.price * (1 + self.stepMap[step + 1] / 100)
                limitOrder = ShortLimitOrder(self.cl, self.symbol)
                limitOrder.open(position.qty / limitPrice, limitPrice)
                limitOrder.Update()
                print('\n', position, '\n', limitOrder)
            if limitOrder.status == 'Filled' and step == 7:
                print('\n', position, '\n', limitOrder)
                position.takeProfit80()
                print('Step 8')
                step += 1
                print('\n', position, '\n', limitOrder)
                continue
            await asyncio.sleep(1)


    async def longAlgo(self):
        startPrice = self.tokenPrice()
        print(f'longAlgo startPrice {startPrice}')
        step = 1
        baseDepo = self.depo / startPrice

        position = LongPosition(self.cl, self.symbol, self.leverage)
        print(f'longAlgo position {position}')
        position.Update()
        if position.price != 0:
            print('Long pos exists!')
            position.takeProfit()

            print('Long tp corrected')
            limitOrder = LongLimitOrder(self.cl, self.symbol)
            limitOrder.findncancel()
            print('Long limit orders have been canceled')
            start_qty = baseDepo * self.valueMap[1]
            # print(start_qty, position.qty)

            print(start_qty, position.price, startPrice, position.qty, 
                  start_qty * startPrice, start_qty * position.price)
            startValueUsdt = start_qty * startPrice
            ratio = position.qty / startValueUsdt
            from math import log
            step = round(log(ratio, 2), 0) + 1

            marketOrder = LongMarketOrder(self.cl, self.symbol)
            marketOrder.price = position.price
            print('Long step', step)
        else:
            qty = baseDepo * self.valueMap[1]
            marketOrder = LongMarketOrder(self.cl, self.symbol)
            marketOrder.open(qty)
            print(marketOrder)

            position = LongPosition(self.cl, self.symbol, self.leverage)
            position.Update()
            position.takeProfit()
            print(position)


        limitQty = baseDepo * self.valueMap[step + 1]
        limitPrice = marketOrder.price * (1 - self.stepMap[step + 1] / 100)
        limitOrder = LongLimitOrder(self.cl, self.symbol)
        limitOrder.open((position.qty) / limitPrice, limitPrice)
        print('\t' * 2, position.qty, position.price, startPrice)
        print(limitOrder)
        await asyncio.sleep(1)

        while True:
            # print('Long', step)
            limitOrder.Update()
            position.Update()
            if position.price == 0:
                print('\n', position, '\n', limitOrder)
                limitOrder.findncancel()
                print('\n', position, '\n', limitOrder)
                print('long pos is null')
                return
            if not position.tp:
                position.takeProfit()
                self.tprecoveryMSG()
            if limitOrder.status == 'Cancelled' and step < 7:
                print('\n', position, '\n', limitOrder, 'short limit irder filled')
                self.limitrecoveryMSG()

                limitPrice = limitOrder.price
                limitQty = limitOrder.qty
                limitOrder = LongLimitOrder(self.cl, self.symbol)
                limitOrder.open(limitQty, limitPrice)
                limitOrder.Update()
                print('\n', position, '\n', limitOrder)

            if limitOrder.status == 'Filled' and step < 7:
                print('\n', position, '\n', limitOrder, 'long limit irder filled')
                position.Update()
                position.takeProfit()
                limitOrder.findncancel()
                step += 1

                limitQty = baseDepo * self.valueMap[step + 1]
                limitPrice = marketOrder.price * (1 - self.stepMap[step + 1] / 100)
                limitOrder = LongLimitOrder(self.cl, self.symbol)
                limitOrder.open(position.qty / limitPrice, limitPrice)
                limitOrder.Update()
                print('\n', position, '\n', limitOrder)
            if limitOrder.status == 'Filled' and step == 7:
                print('\n', position, '\n', limitOrder)
                position.takeProfit80()
                print('Step 8')
                step += 1
                print('\n', position, '\n', limitOrder)
                continue
            await asyncio.sleep(1)

    async def shortLoop(self):
        while True:
            # await self.shortAlgo()
            print('Short Algo started')
            self.cl.cancel_all_limit_orders(self.symbol, 'Sell')
            print('Short limits cancelled')
            try:
                await self.shortAlgo()
            except BaseException as e:
                print(e)
            print('Short Algo ended')

            self.checkPnL("Buy")

    async def longLoop(self):
        # while True:
        #     await self.longAlgo()
        while True:
            print('Long Algo started')
            self.cl.cancel_all_limit_orders(self.symbol, 'Buy')
            print("long limits cancelled")
            try:
                await self.longAlgo()
            except BaseException as e:
                print(e)
            print('Long Algo ended')

            self.checkPnL("Sell")


    def checkPnL(self, side):
        closedPnL = self.cl.get_closed_PnL_symbol(self.symbol)['result']['list']
        for pos in closedPnL:
            if pos['side'] == side:
                pnlvalue = float(pos['closedPnl'])
                print('\t\t\t', pos)
                if pnlvalue < 0:
                    tgmsg = {
                        'Type': "PnL",
                        'User Id': self.uid,
                        'symbol': self.symbol,
                        'PnL': pnlvalue
                    }
                    import json
                    import time
                    
                    t = time.time()
                    with open('main/tgmsgs/' + str(t), "w") as fp:
                        json.dump(tgmsg , fp)
                    break
                break

    def tprecoveryMSG(self):
        tgmsg = {
            'Type': "TakeProfit",
            'User Id': self.uid,
            'symbol': self.symbol,
        }
        import json
        import time
                    
        t = time.time()
        with open('main/tgmsgs/' + str(t), "w") as fp:
            json.dump(tgmsg , fp)

    def limitrecoveryMSG(self):
        tgmsg = {
            'Type': "Limit",
            'User Id': self.uid,
            'symbol': self.symbol,
        }
        import json
        import time
                    
        t = time.time()
        with open('main/tgmsgs/' + str(t), "w") as fp:
            json.dump(tgmsg , fp)

    def geventEngineStart(self):
        import gevent

        gevent.joinall([
            gevent.spawn(self.shortLoop),
            gevent.spawn(self.longAlgo)
        ])

    async def asyncEngineStart(self):
        self.cl.switch_position_mode(self.symbol, 3)

        print(self.valueMap)

        task1 = asyncio.create_task(self.longLoop())
        task2 = asyncio.create_task(self.shortLoop())

        await task1
        await task2

