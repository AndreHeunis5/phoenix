
class Phoenix:
    """
    Sets up and runs backtests
    """
    def __init__(self, strategy, broker, num_stocks):
        """

        :param strategy:    The trading strategy
        :param broker:      Instance of the broker class Rules for interacting with the broker (commission etc)
        """
        self.strategy = strategy
        self.broker = broker
        self.num_stocks = num_stocks

        self.stocks_data = {}               # Dict for holding the price data for each stock in the trading universe
        self.asx200_dateranges = []         # List of date ranges and the corresponding asx200 constituents

    def add_stock(self, stock_data, stock_name):
        """


        :param pandas.core.frame.DataFrame stock_data:
        :param str stock_name:
        :return:
        """
        self.stocks_data[stock_name] = stock_data

    def add_asx200_def(self, date_ranges):
        """

        Raises a value error if there aren't exactly self.num_stocks stocks in each date range

        :param list date_ranges:    A list of type backtest.AsxDateRange
        """
        # Check for self.num_stocks stocks in each date range
        for r in date_ranges:
            if len(r.stocks) != self.num_stocks:
                raise ValueError("{} stocks in date range {}. Should be {}".format(len(r.stocks), r.date_range, self.num_stocks))

        self.asx200_dateranges = date_ranges

    def run_backtest(self):
        """

        :return:
        """
        # Loop through date ranges
        for dr_i, dr in enumerate(self.asx200_dateranges):
            start_date = dr.date_range.start_date
            end_date = dr.date_range.end_date
            dr_stock_names = dr.stocks

            # Select relevant stocks
            print(self.stocks_data.keys())
            dr_stocks_data = {sname: self.stocks_data[sname] for sname in dr_stock_names}

            # Clear signals from the previous date range and warm up any trading signals that require it
            trading_dates = self.strategy.reset(dr_stocks_data, start_date, end_date)

            # Loop through dates in date range
            for td in trading_dates:
                print('-' * 20)
                print(td)

                # broker executes buy and sell orders on open prices
                # TODO: be able to execute on close or open
                self.broker.execute_orders(dr_stocks_data, td)

                # calculate signals for current date
                self.strategy.generate_trading_signals(dr_stocks_data, td)

                # pass signals to portfolio balancer that will generate buy and sell signals
                trades_to_order = self.strategy.generate_orders()

                # pass trades to the broker
                self.broker.order_trades(trades_to_order)

                self.broker.update_portfolio_value(dr_stocks_data, td)        # TODO implement


            # TODO close positions that arent in the next date range

        #     # TODO store everything we need for plotting / analysis before moving on to the next date range and resetting everything

        # Run final analysis and visualisation
        self.broker.show_backtest_results(self.stocks_data, self.strategy)


