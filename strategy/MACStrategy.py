# Dummy strategy to use while building the repo

import logging
import pandas as pd

from strategy.GenericStrategy import GenericStrategy
from broker.Order import Order
from broker.OrderType import OrderType


class MACStrategy(GenericStrategy):
    """
    Toy moving average crossover strategy.
    """

    def __init__(self, short_ema_period, long_ema_period, logger):
        """
        :param short_ema_period:    EMA period in days
        :param long_ema_period:     EMA period in days
        """
        self.name = 'MACStrategy'

        # Calculate the alphas required for the specified time ranges
        self.alpha_short = self.__get_ema_alpha(short_ema_period)
        self.alpha_long = self.__get_ema_alpha(long_ema_period)

        self.stock_indicators = {}          # short and long ema for each stock
        self.stock_trading_signals = {}     # trading signal for each stock (-1 for sell, +1 for buy)

        self.logger = logger

    def __get_ema_alpha(self, period):
        """
        :param period:      Smoothing amount in days
        :return:            EMA alpha for the specified time period
        """
        return 2.0 / (period + 1)

    def __ema(self, vt, ema, alpha):
        """
        :param vt:      Unsmoothed value at the new time step
        :param ema:     EMA value from the previous time step
        :param alpha:   Alpha value to weight new value
        :return:        New average
        """
        return (vt - ema) * alpha + ema

    def reset(self, stock_data, start_date, end_date):
        """


        :param dict stock_data:     Price data for each stock
        :return:                    list of trading dates
        """
        self.stock_indicators = {}
        trading_dates = None

        # TODO warm up short and long MAC here
        # TODO use a better way of getting all the trading dates
        # TODO initialise better, check for history
        for s, sd in stock_data.items():

            # initialise indicators
            self.stock_indicators[s] = {}
            self.stock_indicators[s]['sma'] = pd.Series(sd['close'].values[0], [start_date])  # TODO appending to pandas series is very inefficient
            self.stock_indicators[s]['lma'] = pd.Series(sd['close'].values[0], [start_date])

            # initialise trading signals
            self.stock_trading_signals[s] = []

            trading_dates = sd.index.values

        trading_dates = [td for td in trading_dates if start_date <= td <= end_date]

        return trading_dates

    def generate_trading_signals(self, data, date):
        """
        Generate the trading signals. TODO risk model here?

        Values in the trading signal are: TODO values should be number of shares (base on risk model / position sizing)
            1:  Buy
            -1: Sell
            0:  No action

        :param dict data:   Dict containing close prices for each stock on "date"
        :param date:        Date corresponding to the close prices in "data"
        """
        # Update indicators and signals
        for s, prices in data.items():

            price = prices.loc[date]['close']

            # Update short ema
            prev_short = self.stock_indicators[s]['sma'].values[-1]
            new_short = self.__ema(price, prev_short, self.alpha_short)
            self.stock_indicators[s]['sma'] = self.stock_indicators[s]['sma'].append(pd.Series([new_short], index=[date]))

            # Update long ema
            prev_long = self.stock_indicators[s]['lma'].values[-1]
            new_long = self.__ema(price, prev_long, self.alpha_long)
            self.stock_indicators[s]['lma'] = self.stock_indicators[s]['lma'].append(pd.Series([new_long], index=[date]))

            # Update trading signal
            if prev_short <= prev_long and new_short > new_long:
                self.stock_trading_signals[s].append(1)
            elif prev_short > prev_long and new_short <= new_long:
                self.stock_trading_signals[s].append(-1)
            else:
                self.stock_trading_signals[s].append(0)

    def generate_orders(self):
        """
        Generate trade orders based on the trading signals and sizes calculated in "generate_trading_signals"

        :return:    List of orders to be executed at the start of the next time step
        """
        orders = []

        for s, signal in self.stock_trading_signals.items():

            order_type = None

            if signal[-1] > 0:
                order_type = OrderType.buy
                self.logger.info("STRATEGY: Generated buy order")
            elif signal[-1] < 0:
                order_type = OrderType.sell
                self.logger.info("STRATEGY: Generated sell order")

            orders.append(Order(stock_name=s, type=order_type, num_of_shares=20))

        return orders
