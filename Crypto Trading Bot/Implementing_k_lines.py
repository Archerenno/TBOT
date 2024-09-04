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

operating_mins = 450
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
    #computes the K-Lines here and reports whether its a buy or a sell signal 
    candles = client.get_klines(symbol = 'BTCUSDT', interval = client.KLINE_INTERVAL_1MINUTE)
    # The latest candles info from here is always put at the front, hence i call the candles[-1] to get the latest info which is good
    #  and doesn't require us to pop any information off the list and can just keep calling, from the candles list which is updated with the desired interval

    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[-1] 

    print(open_time)

    """thinking of working with these candles and look at the last three. if the first close is higher than the open then continue into the next candle
    and the close is higher than the close of the other candle continue into the next candle. 
    then if the close of the third candle 
    so call candles[-3] check this first. and it will change a boolean  of buy or sell to true or false
    then call candles[-2] and if it has the same boolean identity as candles[-3]
    continue to candles[-1] and if it has the same as the other 2 it can then recommend a buy or sell to the other parts of the code. 
    """
    #This chooses the candle to start with so if its -5 it will start 5 candles back etc. 
    candle_index = -5
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index]
    current_close = close_price
    current_open = open_price
    signal = []
    bearish = []


    while candle_index < 0:
        open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index]
        if current_close < close_price:
            print(current_close)
            print(close_price)

            current_close = close_price
            print(current_close)
            signal.append(True)

        else:
            current_close = close_price
            signal.append(False)
        candle_index += 1 


    buy_signal_counter = 0 
    for signals in signal:
        if signals == True:
            buy_signal_counter += 1 
        else:
            buy_signal_counter -= 1 

    # In this method here this is returning the signal that the K lines have given.
    # 0 means Neutral 
    # -1 means Slightly Bearish 
    # -2 means Bearish 
    # 1 means Slightly Bullish 
    # 2 means Bullish 
    # these values would only work when 5 k lines as if theres only 3 k lines being looked
    # theres never 
    print(signal)
    if buy_signal_counter == 0:
        k_line_signal = 0
    elif buy_signal_counter < 0 and buy_signal_counter > -3:
        k_line_signal = -1
    elif buy_signal_counter <= -3:
        k_line_signal = -2
    elif buy_signal_counter > 0 and buy_signal_counter < 3:
        k_line_signal = 1 
    else:
        k_line_signal = 2 


    print(k_line_signal)
    



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



