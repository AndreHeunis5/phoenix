# Dummy strategy to use while building the repo

import logging
import backtrader as bt


class TestStrategy(bt.Strategy):

    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataclose1 = self.datas[1].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        self.sma1 = bt.indicators.SimpleMovingAverage(self.datas[1], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Get trade signals for each stock
        dummy_signal_holder = []
        for data in enumerate(self.datas):
            dummy_signal_holder.append(self.get_trade_signals(data))

        # # Run risk model
        # refined_orders = self.run_risk_model(dummy_signal_holder)
        #
        # # Buy and sell in proportions determined by the risk model
        # self.enter_orders(refined_orders)

    def get_trade_signals(self, data):
        """


        :return:
        """
        ind = data[0]
        data = data[1]

        # TODO: move order submissions to later in the pipeline
        if self.sma < self.data.close:
            self.log('buy {}'.format(self.getdatanames()[ind]))
            submitted_order = self.buy(data=data, size=10)
            # print("current position: {}".format(self.getposition(data)))

        elif self.sma > self.data.close:
            self.log('sell {}'.format(self.getdatanames()[ind]))
            submitted_order = self.sell(data=data, size=10)
            # print("current position: {}".format(self.getposition(data)))

    def enter_orders(self, orders):
        """

        :param orders:
        :return:
        """
        return orders
