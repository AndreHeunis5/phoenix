# Library for visualising / printing results of a backtest

import pyfolio as pf
import pandas as pd
import logging


# TODO: change filename to have info about the run
def init_logging(should_output_to_console, should_output_to_file):
    """
    Initialise loggers for logging INFO level messages to file and console

    :param should_output_to_console:    Boolean indicating whether info logs should be written to console
    :param should_output_to_file:       Boolean indicating whether info logs should be written to console
    """
    # set up logging to file
    if should_output_to_file:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s \t\t %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='backtest/logs/backtest_log.txt',
                            filemode='w')

    # set up logging to console
    if should_output_to_console:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s \t\t %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


def run_pyfolio_stuff(results):
    """
    DOESNT WORK YET!!!

    :param results: ---
    :return:        ---
    """

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