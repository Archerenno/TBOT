import pandas as pd
import numpy as np
from binance.client import Client
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()


# Binance API setup (Set your API key & secret here)
API_KEY = os.getenv("API_PUBLIC")
API_SECRET = os.getenv("API_PRIVATE")

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url


# Function to get historical data from Binance
def fetch_binance_data(symbol="BTCUSDT", interval="1h", lookback="30 days ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                       'close_time', 'quote_asset_volume', 'num_trades', 
                                       'taker_buy_base', 'taker_buy_quote', 'ignore'])
    
    # Convert timestamp to datetime and set as index
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('datetime', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    
    return df


# Ichimoku Cloud Indicator Calculation
def ichimoku_cloud(df, tenkan_period=9, kijun_period=26, senkou_b_period=52):
    # Tenkan-sen (Conversion Line)
    df['tenkan'] = (df['high'].rolling(window=tenkan_period).max() + df['low'].rolling(window=tenkan_period).min()) / 2
    # Kijun-sen (Base Line)
    df['kijun'] = (df['high'].rolling(window=kijun_period).max() + df['low'].rolling(window=kijun_period).min()) / 2
    # Senkou Span A (Leading Span A)
    df['senkou_a'] = ((df['tenkan'] + df['kijun']) / 2).shift(kijun_period)
    # Senkou Span B (Leading Span B)
    df['senkou_b'] = (df['high'].rolling(window=senkou_b_period).max() + df['low'].rolling(window=senkou_b_period).min()) / 2
    df['senkou_b'] = df['senkou_b'].shift(kijun_period)
    # Chikou Span (Lagging Span)
    df['chikou'] = df['close'].shift(-kijun_period)
    
    return df


# Trading signals based on Ichimoku Cloud
def ichimoku_signals(df):
    signals = []
    
    for i in range(len(df)):
        # Buy Signal: Tenkan crosses above Kijun, and price is above the Cloud
        if df['tenkan'][i] > df['kijun'][i] and df['close'][i] > max(df['senkou_a'][i], df['senkou_b'][i]):
            signals.append('BUY')
        # Sell Signal: Tenkan crosses below Kijun, and price is below the Cloud
        elif df['tenkan'][i] < df['kijun'][i] and df['close'][i] < min(df['senkou_a'][i], df['senkou_b'][i]):
            signals.append('SELL')
        else:
            signals.append('HOLD')
    
    df['signal'] = signals
    return df


# Function to plot Ichimoku Cloud and trading signals
def plot_ichimoku(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot closing price
    ax.plot(df.index, df['close'], label="Close Price", color='blue', alpha=0.6)
    
    # Plot Ichimoku Cloud
    ax.fill_between(df.index, df['senkou_a'], df['senkou_b'], where=(df['senkou_a'] > df['senkou_b']),
                    color='green', alpha=0.3, label="Cloud (Bullish)")
    ax.fill_between(df.index, df['senkou_a'], df['senkou_b'], where=(df['senkou_a'] < df['senkou_b']),
                    color='red', alpha=0.3, label="Cloud (Bearish)")
    
    # Plot Tenkan, Kijun, and Chikou lines
    ax.plot(df.index, df['tenkan'], label="Tenkan (Conversion Line)", color='red')
    ax.plot(df.index, df['kijun'], label="Kijun (Base Line)", color='orange')
    ax.plot(df.index, df['chikou'], label="Chikou (Lagging Span)", color='green')

    # Highlight Buy/Sell signals
    buy_signals = df[df['signal'] == 'BUY']
    sell_signals = df[df['signal'] == 'SELL']
    
    ax.plot(buy_signals.index, buy_signals['close'], '^', markersize=10, color='green', label="Buy Signal")
    ax.plot(sell_signals.index, sell_signals['close'], 'v', markersize=10, color='red', label="Sell Signal")
    
    ax.set_title('Ichimoku Cloud and Trading Signals')
    ax.legend(loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Main function to run the bot
def run_ichimoku_bot():
    # Fetch historical data from Binance (1 hour intervals for the last 30 days)
    symbol = "BTCUSDT"
    df = fetch_binance_data(symbol, interval="1h", lookback="30 days ago UTC")
    
    # Calculate Ichimoku Cloud
    df = ichimoku_cloud(df)
    
    # Generate trading signals
    df = ichimoku_signals(df)
    
    # Print the latest signal
    latest_signal = df['signal'].iloc[-1]
    print(f"Latest Signal: {latest_signal}")
    
    # Plot the Ichimoku Cloud and signals
    plot_ichimoku(df)


# Run the bot
run_ichimoku_bot()
