# Read / write access for backtest data

import datetime
import backtrader as bt


class Repository:

    def __init__(self, dir):
        self.dir = dir

    # TODO: rewrite to load data produced by etl
    def get_backtest_data(self, cerebro):
        """
        dummy function to load data

        :param cerebro: Cerebro instance to add data to
        """
        # Create a Data Feed
        data0 = bt.feeds.YahooFinanceCSVData(
            dataname=self.dir + 'orcl-1995-2014.txt',
            fromdate=datetime.datetime(2000, 1, 1),
            todate=datetime.datetime(2000, 3, 31),
            reverse=False)

        data1 = bt.feeds.YahooFinanceCSVData(
            dataname=self.dir + 'yhoo-1996-2014.txt',
            fromdate=datetime.datetime(2000, 1, 1),
            todate=datetime.datetime(2000, 3, 31),
            reverse=False)

        cerebro.adddata(data0, name='data0')
        cerebro.adddata(data1, name='data1')
