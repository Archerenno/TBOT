import pandas as pd
import requests
import backtrader as bt

def get_binance_klines(symbol, interval, limit = 240):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url).json()

    df = pd.DataFrame(response, columns=[
        "timestamp", "open", "high", "low", "close", "volume", 
        "close_time", "quote_asset_volume", "num_trades", 
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])

    # Convert timestamp to readable datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    
    # Keep only necessary columns
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    
    # Save to CSV
    df.to_csv("lazio_1m_data.csv", index=False)
    print("Data saved to binance_1m_data.csv")

    
    
    
    

# Run the function
get_binance_klines('LAZIOUSDT', '1m')
file = "lazio_1m_data.csv"





# Define a strategy
class SMACrossStrategy(bt.Strategy):
    params = (("fast_period", 5), ("slow_period", 10))  # Set periods for SMAs

    def __init__(self):
        # Define the two SMAs
        self.sma_fast = bt.indicators.MovingAverageSimple(self.data.close, period=self.params.fast_period)
        self.sma_slow = bt.indicators.MovingAverageSimple(self.data.close, period=self.params.slow_period)
        self.amount = 0

    def next(self):
        # Buy when fast SMA crosses above slow SMA
        if self.sma_fast[0] > self.sma_slow[0] and self.sma_fast[-1] <= self.sma_slow[-1]:
            if not self.position:  # Check if we already have a position
                port_size = cerebro.broker.getvalue()
                curr_price = self.data.close[0]
                self.amount = port_size / curr_price
                self.buy(size = self.amount)
                print(f"BUY @ {self.data.close[0]} on {self.data.datetime.date(0)}")

        # Sell when fast SMA crosses below slow SMA
        elif self.sma_fast[0] < self.sma_slow[0] and self.sma_fast[-1] >= self.sma_slow[-1]:
            if self.position:  # Check if we are currently in a position
                self.sell(size = self.amount)
                print(f"SELL @ {self.data.close[0]} on {self.data.datetime.date(0)}")

# Initialize Backtrader
cerebro = bt.Cerebro()

# Add strategy
cerebro.addstrategy(SMACrossStrategy)

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
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0)

# Run the backtest
print("Starting Portfolio Value:", cerebro.broker.getvalue())
cerebro.run()
print("Final Portfolio Value:", cerebro.broker.getvalue())

# Plot the results
cerebro.plot()
