import time
from multiprocessing import Process

from bingx_w.bingxAPI import Client


class Dispatcher:
    rule_for_value = {1: 0.2,
                      2: 0.2,
                      3: 0.4,
                      4: 0.8,
                      5: 1.6,
                      6: 3.2,
                      7: 6.4,
                      8: 12.8}

    rule_for_step = {1: 0,
                     2: 0.3,
                     3: 0.8,
                     4: 1.8,
                     5: 3.2,
                     6: 6,
                     7: 10,
                     8: 1.5}

    def __init__(self, cl: Client, symbol: str, leverage):
        self.max_step = len(self.rule_for_step)
        self.step = 0  # count of completed orders
        self.history = {}

        self.cl = cl
        self.symbol = symbol
        self.start_bal = cl.user_balance()
        self.start_bal_2 = -1
        self.leverage = leverage
        cl.set_leverage(symbol=self.symbol,
                        side='SHORT',
                        leverage=self.leverage)
        cl.set_leverage(symbol=self.symbol,
                        side='LONG',
                        leverage=self.leverage)

    def get_stop_price(self, price):
        return price - 10 / self.leverage, price + 10 / self.leverage

    def form_qty(self, value_in_percents):
        return self.start_bal_2 * value_in_percents / 100

    def get_history_price(self):
        if not self.history:
            return -1
        # print(self.history)
        return self.history[self.step - 1]

    def work(self):
        while True:
            new_price = self.cl.last_price(self.symbol)
            print(f'self.step = {self.step}')
            if not new_price:
                print("Перегрузка")
                time.sleep(1)
                continue
            self.start_bal_2 = self.start_bal / new_price
            if self.step == 0:  # There were no orders
                resp1 = self.cl.place_order(symbol=self.symbol,
                                            side='BUY',
                                            quantity=self.form_qty(self.rule_for_value[1]),
                                            stopPrices=self.get_stop_price(new_price))
                resp2 = self.cl.place_order(symbol=self.symbol,
                                            side='SELL',
                                            quantity=self.form_qty(self.rule_for_value[1]),
                                            stopPrices=self.get_stop_price(new_price))
                print("BUY", resp1)
                print("SELL", resp2)
                ######
                # resp = self.cl.bulk_orders_bs(symbol=self.symbol,
                #                               quantity=self.form_qty(self.rule_for_value[1]))
                # print(resp)
                ######
                self.history[1] = new_price
                self.step = 1
            elif self.step == len(self.rule_for_value):  # last step has been complete
                print("STOP")
                self.step = 0
            else:
                past_price = self.history[self.step]
                if abs(1 - new_price / past_price) > self.rule_for_step[self.step + 1] / 100:
                    if new_price > past_price:
                        resp = self.cl.place_order(symbol=self.symbol,
                                                   side='SELL',
                                                   quantity=self.form_qty(self.rule_for_value[self.step + 1]),
                                                   stopPrices=self.get_stop_price(new_price))
                    else:
                        resp = self.cl.place_order(symbol=self.symbol,
                                                   side='BUY',
                                                   quantity=self.form_qty(self.rule_for_value[self.step + 1]),
                                                   stopPrices=self.get_stop_price(new_price))
                    print(resp)
                    self.step += 1
                    self.history[self.step] = new_price
                else:
                    print(f'\t\t{abs(1 - new_price / past_price) * 100}%')
                    time.sleep(1)
