
import pandas as pd
from pylab import *
import seaborn as sns

from broker.Position import Position
from broker.OrderType import OrderType

sns.set()


class Broker:
    """
    Keeps track of and controls

        - Portfolio value and constituents
        - Buy and sell orders and order execution

    Takes an instance of the t_cost_model class that models transaction costs for the backtest
    """

    def __init__(self, starting_cash, t_cost_model, logger):
        """
        :param float starting_cash:         Total cash in the trading account at the start of the test
        :param TCostModel t_cost_model:     An instance of TCostModel
        """
        self.cash = starting_cash
        self.t_cost_model = t_cost_model
        self.open_positions = {}        # Open positions of type broker.position
        self.pending_sell_orders = []
        self.pending_buy_orders = []

        # Structure for storing backtest history at each timestep
        self.backtest_history = pd.DataFrame(columns=["cash", "portfolio_value"])
        self.executed_buy = {}
        self.executed_sell = {}
        self.trade_profits = []         # TODO combine with executed_sell somehow?
        self.num_winning_trades = 0     # The number of times any number of shares were sold for a profit

        self.logger = logger

    def execute_orders(self, stocks_data, td):
        """
        Execute orders that were entered after the previous time step

        NOTE: short orders / positions are currently not supported

        :param stocks_data:     Dict containing DataFrames for each stock. Dataframe fields include
                                    - 'close'
                                    - 'open'
        :param td:              Date on which the trade orders are being executed
        """

        # TODO: Transaction cost model

        # First execute sell orders to free up cash for buys
        while self.pending_sell_orders:
            sell_order = self.pending_sell_orders.pop()
            sn = sell_order.stock_name

            # TODO check that the sale is valid (position exists etc)
            current_stock_value = stocks_data[sn]["open"][td]
            self.cash += current_stock_value * sell_order.num_of_shares
            new_position_size = self.open_positions[sn].num_of_shares - sell_order.num_of_shares

            # Record the sell action
            if sn not in self.executed_sell.keys():
                self.executed_sell[sn] = pd.Series([current_stock_value], index=[td])
            else:
                self.executed_sell[sn] = self.executed_sell[sn].append(pd.Series([current_stock_value], index=[td]))
            self.num_winning_trades += current_stock_value > self.open_positions[sn].buy_price.values[0]
            self.trade_profits.append(
                sell_order.num_of_shares * (current_stock_value - self.open_positions[sn].buy_price.values[0]))

            # if the amount sold == the current position size, close the position
            if new_position_size == 0:
                del self.open_positions[sn]
            else:
                self.open_positions[sn].num_of_shares -= sell_order.num_of_shares

            self.logger.info("BROKER: Executed sell order")

        # Execute the buy orders
        while self.pending_buy_orders:
            buy_order = self.pending_buy_orders.pop()
            sn = buy_order.stock_name

            # check there is enough cash to execute the trade
            current_stock_value = stocks_data[sn]["open"][td]
            cash_required = current_stock_value * buy_order.num_of_shares

            # position sizing should ensure this never happens but just to be sure...
            if cash_required > self.cash:
                # log a missed trade
                print("not enough cash for BUY trade: stock: {} value: {} count: {} current cash: {}"
                      .format(sn, stocks_data[sn]["open"][td], buy_order.num_of_shares, self.cash))
                continue

            self.cash -= cash_required

            # If there is no existing position for the stock, create one. Else update the existing one
            if sn in self.open_positions:
                bp_old = self.open_positions[sn].buy_price
                num_old = self.open_positions[sn].num_of_shares
                bp_new = stocks_data[sn].open
                num_new = buy_order.num_of_shares

                weighted_avg_buy_price = (bp_old * num_old + bp_new * num_new) / (num_old + num_new)

                self.open_positions[sn] = Position(
                    num_of_shares=self.open_positions[sn].num_of_shares + buy_order.num_of_shares,
                    buy_price=weighted_avg_buy_price)
            else:
                self.open_positions[sn] = Position(
                    num_of_shares=buy_order.num_of_shares,
                    buy_price=stocks_data[sn].open)     # TODO: buying on the open price?

            # Record the buy action
            if sn not in self.executed_buy.keys():
                self.executed_buy[sn] = pd.Series([current_stock_value], index=[td])
            else:
                self.executed_buy[sn] = self.executed_buy[sn].append(pd.Series([current_stock_value], index=[td]))
            self.logger.info("BROKER: Executed buy order")

        self.update_portfolio_value(stocks_data, td)

    def order_trades(self, trades_to_order):
        """
        Submit the orders required to re-balance the portfolio for the current time step

        :param list trades_to_order:    List of broker.Order objects. Trades to order for execution on the following
                                        time step
        """
        for t in trades_to_order:
            if t.type == OrderType.buy:
                self.pending_buy_orders.append(t)
                self.logger.info("BROKER: Entered buy order")
            elif t.type == OrderType.sell:
                self.pending_sell_orders.append(t)
                self.logger.info("BROKER: Entered sell order")

    def update_portfolio_value(self, stocks_data, date):
        """
        Update the instance's records of the total portfolio value

        :param dict stocks_data:    Dict containing dataframes for each stock
        :param date:                Date that the current update is for
        """
        position_value = 0
        for s, pos in self.open_positions.items():
            #TODO: use close?
            position_value += stocks_data[s]['close'].loc[date] * pos.num_of_shares

        full_value = self.cash + position_value
        self.backtest_history.loc[date] = [self.cash, full_value]

        # self.backtest_history.append(
        #     pd.DataFrame([self.cash, full_value],
        #                  index=[date],
        #                  columns=['cash', 'portfolio_value']))

    def show_backtest_results(self, full_stock_data, strategy):
        """
        Display the final results for the backtest

        :param full_stock_data:     Dict containing dataframes for each stock. Dataframe columns include:
                                        -
        :param strategy:            The strategy instance that was used in the backtest
        """
        portfolio_value = self.backtest_history['portfolio_value']

        # Calculate drawdown
        drawdown = pd.Series(0, index=portfolio_value.index)
        max_val = portfolio_value.values[0]

        for i, v in portfolio_value.iteritems():
            if v > max_val:
                max_val = v
                drawdown.loc[i] = 0.0
            else:
                drawdown.loc[i] = v / max_val - 1.0

        total_trade_count = 0
        for k, v in self.executed_sell.items():
            total_trade_count += len(v)

        tp = np.array(self.trade_profits)
        avg_profit = np.mean(tp)
        median_profit = np.median(tp)
        biggest_profit = np.max(tp)
        biggest_loss = np.min(tp)
        outlier_adjusted_avg_profit = np.mean(tp[tp < np.percentile(tp, 98)])

        # Log final results
        self.logger.info("")
        self.logger.info("------ BACKTEST RESULTS ------")
        self.logger.info("")
        self.logger.info("Final Portfolio Value:\t\t\t\t{:.2f}".format(portfolio_value.values[-1]))
        self.logger.info("Maximum Drawdown:\t\t\t\t\t{:.4f}".format(np.min(drawdown.values)))
        self.logger.info("Sharpe Ratio:\t\t\t\t\t\t{:.4f}".format(0.0))      # TODO populate
        self.logger.info("Total number of trades:\t\t\t{}".format(total_trade_count))
        self.logger.info("Number of winning trades:\t\t\t{}".format(self.num_winning_trades))
        self.logger.info("Average profit per trade:\t\t\t{:.4f}".format(avg_profit))
        self.logger.info("Median profit per trade:\t\t\t{:.4f}".format(median_profit))
        self.logger.info("Largest single winning trade:\t\t{:.4f}".format(biggest_profit))
        self.logger.info("Largest single losing trade:\t\t{:.4f}".format(biggest_loss))
        self.logger.info("Outlier adjusted profit factor:\t{:.4f}".format(outlier_adjusted_avg_profit)) # TODO populate (profit when removing top 2% winners)
        self.logger.info("")
        self.logger.info("------------------------")
        self.logger.info("")

        # Plot portfolio value vs benchmark
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 9))
        ax1.set_title("Portfolio")
        sns.lineplot(data=self.backtest_history['portfolio_value'], ax=ax1, label='portfolio_value', c='orange')

        # TODO plot benchmark on ax1 if there is one

        ax2.set_title("Cash")
        sns.lineplot(data=self.backtest_history['cash'], ax=ax2)

        ax3.set_title("Drawdown")
        sns.lineplot(data=drawdown, ax=ax3)

        # TODO: Move generation of these plots into strategy class
        # Plot stock price and buy / sell events for each stock
        for i, (s, indicators) in enumerate(strategy.stock_indicators.items()):
            fig, ax1 = plt.subplots(figsize=(16, 9))

            # Plot buys for the stock
            if s in self.executed_buy.keys():
                plot(self.executed_buy[s], '^', markersize=10, color='g')

            # Plot sells for the stock
            if s in self.executed_sell.keys():
                plot(self.executed_sell[s], 'v', markersize=10, color='r')

            title(s)
            sns.lineplot(data=full_stock_data[s]['close'], ax=ax1, label=s)
            sns.lineplot(data=indicators['sma'], ax=ax1, label='sma')
            sns.lineplot(data=indicators['lma'], ax=ax1, label='lma')
            legend()

        # Plot distribution of returns from each trade that was made


        show()


