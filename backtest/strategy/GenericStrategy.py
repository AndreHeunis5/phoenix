# Abstract class to force implementation of required functionality

from abc import ABC, abstractmethod, ABCMeta
import backtrader as bt
from backtrader.strategy import MetaStrategy


class FinalMeta(MetaStrategy, ABCMeta):
    pass


class GenericStrategy(ABC, bt.Strategy, metaclass=FinalMeta):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_trade_signal(self, data):
        """

        :return:
        """
        pass

    @abstractmethod
    def enter_orders(self, orders):
        """

        :param orders:
        :return:
        """
        pass