import argparse

import backtrader as bt
import backtrader.feeds as btfeeds

import pandas


def runstrat():
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)



    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='bar', volume=False)


if __name__ == '__main__':
    runstrat()
