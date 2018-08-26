# Library for visualising / printing results of a backtest

import pyfolio as pf
import pandas as pd


def show_outputs(cerebro, results, show_backtrader, show_pyfolio):
    """
    Visualise / print the results of a backtest using the methods provided by the specified packages.

    :param cerebro:             backtrader.Cerebro instance related to the backtest we want to visualise
    :param results:             A list of classes related to strategies used in the backtest
    :param show_backtrader:     Boolean flag indicating whether to show results using backtrader
    :param show_pyfolio:        Boolean flag indicating whether to show results using pyfolio
    """

    if show_backtrader:
        cerebro.plot()

    if show_pyfolio:
        run_pyfolio_stuff(results)


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