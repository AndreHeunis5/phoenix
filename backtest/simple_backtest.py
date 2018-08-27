# Entry point for running a backtest

import backtrader as bt
import logging

from backtest.strategy.TestStrategy import TestStrategy
from backtest.outputs.output_lib import show_outputs, init_logging
from data.Repository import Repository

if __name__ == '__main__':

    init_logging(should_output_to_console=True, should_output_to_file=True)
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
    logging.info('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    results = cerebro.run()

    # Print out the final result
    logging.info('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Show backtest results
    show_outputs(cerebro, results, show_backtrader=True, show_pyfolio=False)

