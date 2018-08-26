# Entry point for running a backtest

import datetime
import backtrader as bt

from backtest.strategy.TestStrategy import TestStrategy
from backtest.outputs.output_lib import show_outputs

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Create a Data Feed
    data0 = bt.feeds.YahooFinanceCSVData(
        dataname='/Users/andreheunis/python_projects/phoenix/data/repo/orcl-1995-2014.txt',
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 3, 31),
        reverse=False)
    cerebro.adddata(data0, name='data0')

    data1 = bt.feeds.YahooFinanceCSVData(
        dataname='/Users/andreheunis/python_projects/phoenix/data/repo/yhoo-1996-2014.txt',
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 3, 31),
        reverse=False)
    cerebro.adddata(data1, name='data1')

    # Initialise the backtest
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)

    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Show backtest results
    show_outputs(cerebro, results, show_backtrader=True, show_pyfolio=False)

