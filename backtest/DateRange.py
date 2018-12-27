
from typing import NamedTuple
import numpy as np


class DateRange(NamedTuple):
    """
    Definition of

    start_date:
    end_date:
    """
    start_date: np.datetime64
    end_date: np.datetime64
