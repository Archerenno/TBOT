from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
import json
from binance.client import Client
from binance.enums import *
import time

# Testnet API credentials
API_KEY = 'rJljPrYroAaNOHIKfy0WJk2xWo9aeAjPsL5YSp2O6JQUTW8E5PU3aIz0hdeX7tO7'
API_SECRET = 'aO0F2T3epauKW9GQGRj4Wlb8zxtCabFXHRE3e3f1nrgANl0FNTMCSkZYQfE6SzT3'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

account = client.get_account()
print(f"Opening account balance is: ${account['balances'][4]['free']}")

operating_mins = 30
last_order_buy = False

for i in range(operating_mins):
    balance = client.get_asset_balance(asset='BTC')
    print(balance)
    bitcoin = TA_Handler(
        symbol="BTCUSD",
        screener="crypto",
        exchange="BINANCE",
        interval=Interval.INTERVAL_1_MINUTE
    )
    analysis = bitcoin.get_analysis()
    print(f"Minute {i}, EMA10: {analysis.moving_averages['COMPUTE']['EMA10']}")
    if analysis.moving_averages['COMPUTE']['EMA10'] == "BUY" and last_order_buy is False:
        # Place a test market order
        symbol = 'BTCUSDT'
        quantity = 0.001
        last_order_buy = True
        try:
            order = client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            print(f"Bought at ${analysis.indicators['open']}")
            # print(order)
        except Exception as e:
            print(f"An error occurred: {e}")
    elif analysis.moving_averages['COMPUTE']['EMA10'] == "SELL" and last_order_buy is True:
        symbol = 'BTCUSDT'
        quantity = 0.001
        last_order_buy = False
        try:
            order = client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            # print(order)
            print(f"Sold at ${analysis.indicators['open']}")
        except Exception as e:
            print(f"An error occurred: {e}")
    time.sleep(60)
print(f"Closing account balance is: ${account['balances'][4]['free']}")



