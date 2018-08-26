# Entry point for running a backtest

import backtrader as bt

from backtest.strategy.TestStrategy import TestStrategy
from backtest.outputs.output_lib import show_outputs
from data.Repository import Repository

if __name__ == '__main__':

    cerebro = bt.Cerebro()
    repo = Repository(dir='/Users/andreheunis/python_projects/phoenix/data/repo/')

    # Add data to the cerebro instance
    repo.get_backtest_data(cerebro=cerebro)

    # Initialise the backtest
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(100000.0)
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

