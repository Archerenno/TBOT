from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
# Import the backtrader platform
import backtrader as bt
import numpy as np


def unix_to_datetime(unix_time):
    if unix_time > 1e10:  # Greater than 10 billion indicates milliseconds
        unix_time /= 1000
    return datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def clean_data(data):
    lines = np.loadtxt("Historical Data/BTCUSDT/11-10-2024/BTCUSDT-1m-2024-11-10.csv", dtype=str)
    for line in lines:
        line_data = line.split(",")
        unix = line_data[0]
        line_data[0] = unix_to_datetime(unix_time=int(unix))

    

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    filepath = "Historical Data/BTCUSDT/11-10-2024/BTCUSDT-1m-2024-11-10.csv"

    clean_data(filepath)

    data = bt.feeds.GenericCSVData(
        dataname = filepath,
        openinterest = -1)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())