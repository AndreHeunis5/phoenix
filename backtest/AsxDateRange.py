
from typing import NamedTuple

from backtest.DateRange import DateRange


class AsxDateRange(NamedTuple):
    """
    Definition of

    where start_date and end_date are .... (type) and stocks_in_the_asx200 is a list of
                                    strings corresponding

    num_of_shares:
    """
    date_range: DateRange
    stocks: list
    # TODO: value when position was opened?