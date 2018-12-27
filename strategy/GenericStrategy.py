from abc import ABC, abstractmethod


class GenericStrategy(ABC):
    """

    """

    @abstractmethod
    def reset(self, stock_data, start_date, end_date):
        """
        Call this function every time the constituents of the trading universe changes.

        Resets the signals from the previous period and warms up trading signals for the new set.

        :param stock_data:
        :param start_date:
        :param end_date:
        :return:
        """
        pass

    @abstractmethod
    def generate_trading_signals(self, stock_data, date):
        """


        :param stock_data:
        :param date:
        :return:
        """
        pass

    @abstractmethod
    def generate_orders(self):
        """
        Using the signals generated in  generate_trading_signals

        :return:
        """
        pass