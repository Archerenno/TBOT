from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
import json
from binance.client import Client
from binance.enums import *

bitcoin = TA_Handler(
    symbol="BTCUSD",
    screener="crypto",
    exchange="BINANCE",
    interval=Interval.INTERVAL_5_MINUTES
)

analysis = bitcoin.get_analysis()
# analysis.moving_averages['COMPUTE']['EMA10']

# Testnet API credentials
API_KEY = 'rJljPrYroAaNOHIKfy0WJk2xWo9aeAjPsL5YSp2O6JQUTW8E5PU3aIz0hdeX7tO7'
API_SECRET = 'aO0F2T3epauKW9GQGRj4Wlb8zxtCabFXHRE3e3f1nrgANl0FNTMCSkZYQfE6SzT3'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

balance = client.get_asset_balance(asset='BTC')
print(balance)

# Place a test market order
symbol = 'BTCUSDT'
quantity = 0.001

try:
    order = client.create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=quantity
    )
    # print(order)
except Exception as e:
    print(f"An error occurred: {e}")
