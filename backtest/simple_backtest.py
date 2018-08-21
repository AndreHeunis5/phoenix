from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import backtrader as bt
import pyfolio as pf
import pandas as pd

from backtest.strategy.TestStrategy import TestStrategy


def run_pyfolio_stuff(results):

    strat = results[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')

    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    print('-- RETURNS')
    print(returns)
    print('-- POSITIONS')
    print(positions)
    print('-- TRANSACTIONS')
    print(transactions)
    print('-- GROSS LEVERAGE')
    print(gross_lev)

    pf.create_full_tear_sheet(
        returns,
        positions=positions,
        transactions=transactions,
        live_start_date='2000-01-01',
        round_trips=True,
        benchmark_rets=pd.Series(1.0, index=returns.index), turnover_denom='portfolio_value')


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

    # run_pyfolio_stuff(results)

    # Plot the result
    cerebro.plot()
