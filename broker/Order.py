
from broker.OrderType import OrderType

from typing import NamedTuple


class Order(NamedTuple):
    """
    Definition of

    stock_name:     Name of the stock that the order relates to
    type:           Whether the order is a buy or sell
    num_of_shares:  Number of shares to buy or sell
    """
    stock_name: str
    type: OrderType
    num_of_shares: int
