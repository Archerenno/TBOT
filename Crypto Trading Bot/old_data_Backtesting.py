import pandas as pd
import requests
import backtrader as bt
from datetime import datetime
import numpy as np

# def get_binance_klines(symbol, interval, limit = 240):
#     url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
#     response = requests.get(url).json()

#     df = pd.DataFrame(response, columns=[
#         "timestamp", "open", "high", "low", "close", "volume", 
#         "close_time", "quote_asset_volume", "num_trades", 
#         "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
#     ])

#     # Convert timestamp to readable datetime
#     df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    
#     # Keep only necessary columns
#     df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    
#     # Save to CSV
#     df.to_csv("lazio_1m_data.csv", index=False)
#     print("Data saved to binance_1m_data.csv")

    
    
def unix_to_datetime(unix_time):
    if unix_time > 1e14:  # Greater than 100 trillion indicates microseconds
        unix_time /= 1e6
    elif unix_time > 1e10:  # Greater than 10 billion indicates milliseconds
        unix_time /= 1e3
    return datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M:%S')


def clean_data(data):
    open_file = open(data + "-CLEAN.csv", "w")
    lines = np.loadtxt(data + ".csv", dtype=str)
    for line in lines:
        line_data = line.split(",")
        unix = line_data[0]
        line_data[0] = unix_to_datetime(unix_time=int(unix))
        open_file.write(",".join(line_data))
        open_file.write("\n")
    open_file.close()

    

# # Run the function
# get_binance_klines('RDNTUSDT', '1m')
# file = "lazio_1m_data.csv"
clean_data("Historical Data/AIXBTUSDT/AIXBTUSDT-1m-2025-02")
file= "Historical Data/MOVEUSDT/MOVEUSDT-1m-2025-02-CLEAN.csv"





# Define a strategy
class SMACrossStrategy(bt.Strategy):

    def __init__(self, fast_period, slow_period):
        # Define the two SMAs
        self.sma_fast = bt.indicators.MovingAverageSimple(self.data.close, period=fast_period)
        self.sma_slow = bt.indicators.MovingAverageSimple(self.data.close, period=slow_period)
        self.amount = 0

    def next(self):
        # Buy when fast SMA crosses above slow SMA
        if self.sma_fast[0] > self.sma_slow[0] and self.sma_fast[-1] <= self.sma_slow[-1]:
            if not self.position:  # Check if we already have a position
                port_size = cerebro.broker.getvalue()
                curr_price = self.data.close[0]
                self.amount = port_size / curr_price
                self.buy(size = self.amount)
                # print(f"BUY @ {self.data.close[0]} on {self.data.datetime.date(0)}")

        # Sell when fast SMA crosses below slow SMA
        elif self.sma_fast[0] < self.sma_slow[0] and self.sma_fast[-1] >= self.sma_slow[-1]:
            if self.position:  # Check if we are currently in a position
                self.sell(size = self.amount)
                # print(f"SELL @ {self.data.close[0]} on {self.data.datetime.date(0)}")



class RSIStrategy(bt.Strategy):

    def __init__(self, low, high):
        self.low_bound = low
        self.high_bound = high
        self.rsi = bt.indicators.RSI(self.data.close, period=14,upperband=self.high_bound, lowerband=self.low_bound)
        self.bought = False
        self.amount = 0
        

    def next(self):
        # print(f"RSI: {self.rsi[0]}")
        if self.rsi[0] < self.low_bound:  # RSI is oversold
            if not self.bought:  # Only buy if no position exists
                # print("BUY @" + self.data.close[0])
                # print(f"RSI: {self.rsi[0]}")
                port_size = cerebro.broker.getvalue()
                curr_price = self.data.close[0]
                self.amount = port_size / curr_price
                self.buy(size = self.amount)
                self.bought = True
        elif self.rsi[0] > self.high_bound:  # RSI is overbought
            if self.bought:  # Only sell if a position exists
                # print("SELL")
                # print(f"RSI: {self.rsi[0]}")
                self.sell(size=self.amount)
                self.bought = False




# Initialize Backtrader
most_profit = [-5000, -1, -1]

for low in range(15, 45):
    for high in range(60, 99):
        # SMACrossStrategy.params.fast_period = fast
        # SMACrossStrategy.params.slow_period = slow

        if high > low:
            cerebro = bt.Cerebro()

            # Add strategy
            cerebro.addstrategy(RSIStrategy, low, high)


            # Load data from the CSV file
            data = bt.feeds.GenericCSVData(
                dataname= file,  # Path to your CSV file
                dtformat="%Y-%m-%d %H:%M:%S",    # Format of the timestamp column in your CSV
                timeframe=bt.TimeFrame.Minutes,   # 1-minute timeframe
                compression=1,                    # 1-minute compression
                openinterest=-1                   # Don't use open interest data
            )

            # Add data to Backtrader
            cerebro.adddata(data)

            # Set starting cash and commission for trades
            cerebro.broker.set_cash(5000)
            cerebro.broker.setcommission(commission=0)

            # Run the backtest
            starting_value = cerebro.broker.getvalue()
            # print("Starting Portfolio Value:", starting_value)
            cerebro.run()
            final_value = cerebro.broker.getvalue()
            print(f"Final Portfolio Value: {final_value}. Low: {low}, High: {high}")
            profit = final_value - starting_value
            if (profit > most_profit[0]) and (profit != 0):
                most_profit = [(final_value - starting_value), low, high]
            # cerebro.plot()
print(most_profit)

# Plot the results
# cerebro.plot()