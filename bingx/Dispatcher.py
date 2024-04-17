import time

from bingxAPI import Client


class Dispatcher:
    rule_for_value = {1: 0.2,
                      2: 0.2,
                      3: 0.4,
                      4: 0.8}

    rule_for_step = {1: 0,
                     2: 0.3,
                     3: 0.8,
                     4: 1.8}

    def __init__(self, cl: Client, symbol: str):
        self.max_step = len(self.rule_for_step)
        self.step = 0
        self.history = {}

        self.cl = cl
        self.symbol = symbol
        self.start_bal = cl.user_balance()

    def form_qty(self, value_in_percents):
        return self.start_bal * value_in_percents / 100

    def get_history_price(self):
        if not self.history:
            return -1
        # print(self.history)
        return self.history[self.step - 1]

    def next(self):
        if self.step == 0:
            self.step = 1
            return ('BUY', 0.2 / 100), ('SELL', 0.2 / 100)
        elif self.step < self.max_step - 1:
            self.step += 1

            return 'BUY', self.rule_for_value[self.step]
        else:
            self.step = 1
            return ('BUY', 0.2 / 100), ('SELL', 0.2 / 100)

    def start(self):
        while True:
            cd = self.next()
            new_price = self.cl.last_price(symbol=self.symbol)
            if self.step == 1:
                side1, value_in_percents1 = cd[0]
                response1 = self.cl.place_order(symbol=self.symbol, side=side1, quantity=self.form_qty(value_in_percents1))
                side2, value_in_percents2 = cd[1]
                response2 = self.cl.place_order(symbol=self.symbol, side=side2, quantity=self.form_qty(value_in_percents2))
                self.history[self.step] = new_price
                print(response1, response2)
            else:
                old_price = self.get_history_price()
                if abs(1 - new_price / old_price) > self.rule_for_step[self.step] / 100:
                    side, value_in_percents = cd
                    response = self.cl.place_order(side=side, quantity=self.form_qty(value_in_percents))
                    self.history[self.step] = new_price
                else:
                    self.step -= 1
                time.sleep(0.1)

