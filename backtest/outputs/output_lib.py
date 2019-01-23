# Library for visualising / printing results of a backtest

import logging
import datetime


# TODO: change filename to have info about the run
def init_logging(should_output_to_console, should_output_to_file):
    """
    Initialise loggers for logging INFO level messages to file and console

    :param should_output_to_console:    Boolean indicating whether info logs should be written to console
    :param should_output_to_file:       Boolean indicating whether info logs should be written to console
    """

    # set up logging to file
    logger = logging.getLogger('backtest_logger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s \t\t %(message)s')

    fh = logging.FileHandler('backtest/logs/backtest_log_{date:%Y%m%d_%H:%M:%S}.txt'.format(date=datetime.datetime.now()))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(console)
    logger.addHandler(fh)

    return logger
