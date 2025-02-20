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
    open_file = open("BTCUSDT-1m-2024-11-10-CLEAN.csv", "w")
    lines = np.loadtxt(data, dtype=str)
    for line in lines:
        line_data = line.split(",")
        unix = line_data[0]
        line_data[0] = unix_to_datetime(unix_time=int(unix))
        open_file.write(",".join(line_data))
        open_file.write("\n")
    open_file.close()


class RSIStrategy(bt.Strategy):
    params = (
        ('high', 70),
        ('low', 30),
        ('period', 14)
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.period,upperband=self.params.high, lowerband=self.params.low)
        self.bought = False



    def next(self):
        # print(f"RSI: {self.rsi[0]}")
        if self.rsi < self.params.low:  # RSI is oversold
            if not self.bought:  # Only buy if no position exists
                print("BUY")
                print(f"RSI: {self.rsi[0]}")
                self.buy(size=10)
                self.bought = True
        elif self.rsi > self.params.high:  # RSI is overbought
            if self.bought:  # Only sell if a position exists
                print("SELL")
                print(f"RSI: {self.rsi[0]}")
                self.sell(size=10)
                self.bought = False



def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    filepath = "Historical Data/BTCUSDT/11-10-2024/BTCUSDT-1m-2024-11-10-CLEAN.csv"

    # clean_data(filepath)

    data = bt.feeds.GenericCSVData(
        dataname = filepath,
        openinterest = -1)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.addstrategy(RSIStrategy, high = 70, low = 30)
    
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: $%.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: $%.2f' % cerebro.broker.getvalue())

main()