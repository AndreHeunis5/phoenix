
import pandas as pd
from pylab import *

from broker.Position import Position
from broker.OrderType import OrderType


class Broker:
    """
    Keeps track of and controls

        - Portfolio value and constituents
        - Buy and sell orders and order execution

    Takes an instance of the t_cost_model class that models transaction costs for the backtest
    """

    def __init__(self, starting_cash, t_cost_model):
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

    def execute_orders(self, stocks_data, td):
        """
        Execute orders that were entered after the previous time step

        NOTE: short orders / positions are currently not supported

        :param stocks_data:     Dict containing DataFrames for each stock
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

            # if the amount sold == the current position size, close the position
            if new_position_size == 0:
                del self.open_positions[sn]
            else:
                self.open_positions[sn].num_of_shares -= sell_order.num_of_shares

            # Record the sell action
            if sn not in self.executed_sell.keys():
                self.executed_sell[sn] = pd.Series([current_stock_value], index=[td])
            else:
                self.executed_sell[sn] = self.executed_sell[sn].append(pd.Series([current_stock_value], index=[td]))

            print("BROKER: Executed sell order")

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
                self.open_positions[sn] = Position(num_of_shares=self.open_positions[sn].num_of_shares + buy_order.num_of_shares)
            else:
                self.open_positions[sn] = Position(num_of_shares=buy_order.num_of_shares)

            # Record the buy action
            if sn not in self.executed_buy.keys():
                self.executed_buy[sn] = pd.Series([current_stock_value], index=[td])
            else:
                self.executed_buy[sn] = self.executed_buy[sn].append(pd.Series([current_stock_value], index=[td]))
            print("BROKER: Executed buy order")

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
                print("BROKER: Entered buy order")
            elif t.type == OrderType.sell:
                self.pending_sell_orders.append(t)
                print("BROKER: Entered sell order")

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

        :param full_stock_data:     Dict containing dataframes for each stock
        :param strategy:            The strategy instance that was used in the backtest
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))
        ax1.set_title("Portfolio")
        ax1.plot(self.backtest_history['portfolio_value'], label='portfolio_value', c='orange')

        for s, data in full_stock_data.items():
            ax = ax1.twinx()
            ax.plot(data['close'])

        ax2.set_title("Cash")
        ax2.plot(self.backtest_history['cash'], label='cash')

        # TODO: Move generation of these plots into strategy class
        for i, (s, indicators) in enumerate(strategy.stock_indicators.items()):
            fig, ax1 = plt.subplots(figsize=(16, 9))

            # Plot buys for the stock
            if s in self.executed_buy.keys():
                plot(self.executed_buy[s], '^', markersize=10, color='g')

            # Plot sells for the stock
            if s in self.executed_sell.keys():
                plot(self.executed_sell[s], 'v', markersize=10, color='r')

            title(s)
            plot(full_stock_data[s]['close'], label=s)
            plot(indicators['sma'], label='sma')
            plot(indicators['lma'], label='lma')
            plot()
            legend()

        show()


