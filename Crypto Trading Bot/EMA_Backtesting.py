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
file= "Historical Data/BTCUSDT/25-2-2025/BTCUSDT-1m-2025-02-25-CLEAN.csv"





# Define a strategy
class SMACrossStrategy(bt.Strategy):
    params = (("fast_period", 5), ("slow_period", 49))  # Set periods for SMAs

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




# Initialize Backtrader
most_profit = [-5000, -1, -1]

for fast in range(1, 11):
    for slow in range(5, 60):
        # SMACrossStrategy.params.fast_period = fast
        # SMACrossStrategy.params.slow_period = slow
        # NOTE: Code is returning the exact same profit for all values of fast and slow. Something is wrong, fix this

        cerebro = bt.Cerebro()

        # Add strategy
        cerebro.addstrategy(SMACrossStrategy, fast, slow)


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
        print("Final Portfolio Value:", final_value)

        if ((final_value - starting_value) > most_profit[0]) and (fast < slow):
            most_profit = [(final_value - starting_value), fast, slow]
print(most_profit)

# Plot the results
# cerebro.plot()

# clean_data("Historical Data/BTCUSDT/27-2-2025/BTCUSDT-1m-2025-02-27")