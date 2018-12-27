# Entry point for running a backtest


import logging
import pandas as pd
import numpy as np

from backtest.outputs.output_lib import init_logging
from backtest.Phoenix import Phoenix
from backtest.AsxDateRange import AsxDateRange
from backtest.DateRange import DateRange
from broker.Broker import Broker
from broker.TCostModel import TCostModel
from strategy.MACStrategy import MACStrategy


if __name__ == '__main__':

    t_cost_model = TCostModel()
    strategy = MACStrategy(short_ema_period=5, long_ema_period=15)

    broker = Broker(starting_cash=10000.0, t_cost_model=t_cost_model)
    px = Phoenix(strategy=strategy, broker=broker, num_stocks=3)

    # TODO fix this up once all the data assets have a proper ETL
    # Get a pandas dataframe
    datapath = 'data/dataset_20181201.csv'

    # Simulate the header row isn't there if noheaders requested
    skiprows = 0
    header = 0

    dataframe = pd.read_csv(datapath,
                            skiprows=skiprows,
                            header=header,
                            parse_dates=True,
                            index_col=0)  # .fillna(0)

    stocks = dataframe.columns

    for i, s in enumerate(stocks):
        if i == 0:
            continue
        elif i > 3:
            break

        stock_history = dataframe[s].to_frame()
        stock_history.columns = ['close']
        stock_history = stock_history.dropna()  # drop dates where there is no data
        stock_history['open'] = stock_history['close'].shift(1)  # add open prices for buying

        # TODO: remove
        stock_history = stock_history.dropna()
        px.add_stock(stock_data=stock_history, stock_name=s)

    # TODO: construct this from file
    # add the date ranges
    px.add_asx200_def(
        date_ranges=[
            AsxDateRange(
                date_range=DateRange(start_date=np.datetime64('2001-09-28'), end_date=np.datetime64('2016-01-31')),
                stocks=['6382285 Equity SEDOL1', '6117960 Equity SEDOL1', '6079695 Equity SEDOL1']
            )])

    px.run_backtest()

