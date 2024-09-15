"""
Archer Simpson
12/9/24
Trading Bot Project - Using a Binance Testnet
"""

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
import json
from binance.client import Client
from binance.enums import *
import time

# Testnet API credentials
# KODI'S KEYS
API_KEY = 'rJljPrYroAaNOHIKfy0WJk2xWo9aeAjPsL5YSp2O6JQUTW8E5PU3aIz0hdeX7tO7'
API_SECRET = 'aO0F2T3epauKW9GQGRj4Wlb8zxtCabFXHRE3e3f1nrgANl0FNTMCSkZYQfE6SzT3'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

#Set global constants
K_LINE_STRONG_BUY = 2
K_LINE_BUY = 1 
K_LINE_STRONG_SELL = -2 
K_LINE_SELL = -1

def print_all_available_coins():
    info = client.get_account()
    all_balances = info['balances']
    print("This is a list of all the available coins through Binance")
    for coin in all_balances:
        print(coin['asset'])


def print_testnet_account_balance(symbol):
    info = client.get_account()
    all_balances = info['balances']
    for coin in all_balances:
        if coin['asset'] == symbol:
            account_balance = coin['free']
    print(f"Official Testnet Account balance ({symbol}): {float(account_balance):.4f}")


def print_coin_information(symbol):
    """NOTE: Only works for LOT_SIZE"""
    coin_info = client.get_symbol_info(symbol)['filters'][1]
    print(f"Coin: {symbol}")
    print(f"Type: {coin_info['filterType']}")
    print(f"    - Minimum Coin you can hold: {coin_info['minQty']}")
    print(f"    - Max Coin you can hold: {coin_info['maxQty']}")
    print(f"    - Step Size (Minimum order amount): {coin_info['stepSize']}")


def EMA_recommendation():
    """
    Returns a bullish/bearish signal using EMA of varying lengths, calculated by trading_view_ta
    """
    bitcoin = TA_Handler(
            symbol="BTCUSD",
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_MINUTE
        )
    analysis = bitcoin.get_analysis()
    return analysis.moving_averages['RECOMMENDATION']


def K_line_initialisation(candle_index):
    """
    The amount of Candles that it analyses must be an odd Integer
    Returns an integer representation of bullish/bearish signals based on the current market candles
    2 = Very Bullish 
    1 = Slightly Bullish
    -1 = Slightly Bearish 
    -2 = Very Bearish 
    """
    #Pulls K-line information from API 
    candles = client.get_klines(symbol = 'BTCUSDT', interval = client.KLINE_INTERVAL_1MINUTE)

    #initialises the current_close 
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index]
    current_close = close_price
    signals = []

    #Loops through the desired amount of candles to gather signals 
    while candle_index < 0:
        open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index + 1]
        if current_close < close_price:
            current_close = close_price
            signals.append(True)
        else:
            current_close = close_price
            signals.append(False)
        candle_index += 1 
    return signals


def K_line_recommendation(signals, candle_index):
    #converting Bool signal into Integer representation 
    buy_signal_counter = 0 

    candles = client.get_klines(symbol = 'BTCUSDT', interval = client.KLINE_INTERVAL_1MINUTE)
    for signal in signals:
        if signal == True:
            buy_signal_counter += 1 
        else:
            buy_signal_counter -= 1 

    if buy_signal_counter < 0 and buy_signal_counter > (candle_index // 2):
        k_line_signal = K_LINE_SELL
    elif buy_signal_counter <= (candle_index // 2):
        k_line_signal = K_LINE_STRONG_SELL
    elif buy_signal_counter > 0 and buy_signal_counter < abs(candle_index // 2 ):
        k_line_signal = K_LINE_BUY
    else:
        k_line_signal = K_LINE_STRONG_BUY
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index]
    current_close = close_price
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[-1]
    signals.pop(0)
    if close_price > current_close:
        signals.append(True)
    else:
        signals.append(False)

    #DELETE THIS PRINT AS THIS IS FOR KODI TO VERIFY ITS WORKING AS IT SHOULD 
    #TESTING PURPOSES ONLY!!!
    print(signals)

    #return final recommendation
    return k_line_signal

def get_last_order_price(symbol):
    trades = client.get_my_trades(symbol = symbol)
    return trades[-1]['price']


def get_current_price(symbol):
    price_info = client.get_all_tickers()
    curr_price = price_info[3]['price']
    return curr_price


def place_market_order(symbol, sell_or_buy, order_size, account_balance):
    if sell_or_buy == 'BUY':
        side_type = SIDE_BUY
    elif sell_or_buy == 'SELL':
        side_type = SIDE_SELL
    try:
            order = client.create_order(
                symbol=symbol,
                side=side_type,
                type=ORDER_TYPE_MARKET,
                quantity=order_size
            )
            order_price = get_last_order_price(symbol)
            account_balance = update_account_balance(sell_or_buy, order_price, order_size, account_balance)
    except Exception as e:
        print(f"An error occurred: {e}")
    return account_balance, order_price


def update_account_balance(sell_or_buy, order_price, order_size, account_balance):
    if sell_or_buy == 'SELL':
        account_balance += float(order_price) * order_size
    else:
        account_balance -= float(order_price) * order_size
    return account_balance


def calculate_trading_profit(closing_balance, starting_account_balance):
    total_profit = closing_balance - starting_account_balance
    if total_profit >= 0:
        return f"TOTAL PROFIT: ${total_profit}"
    else:
        return f"TOTAL PROFIT: -${abs(total_profit)}"


def final_sell(symbol, account_balance, holding_coin, starting_account_balance):
    sell_amount = holding_coin
    if sell_amount > 0:
        closing_balance, order_price = place_market_order(symbol, 'SELL', sell_amount)
        print(f"Sold {sell_amount} of {symbol} at ${order_price}")
    else:
        closing_balance = account_balance
    print(f"Closing Account Balance: ${closing_balance}")
    print('-----------------------------------------------------')
    profit_str = calculate_trading_profit(closing_balance, starting_account_balance)
    print(profit_str)


def run_bot(operating_mins, symbol, starting_balance, max_holding, candle_index, candle_initialisation):
    MAX_HOLDING_COIN = max_holding
    holding_coin = 0
    account_balance = starting_balance
    for i in range(operating_mins):
        current_price = get_current_price(symbol)
        print(f"Currently holding {holding_coin} units of {symbol}, valued at ${float(current_price):.2f} per unit")
        print(f"Account Balance: ${account_balance}")
        buy_recommendation = EMA_recommendation()
        candle_recommendation = K_line_recommendation(candle_initialisation, candle_index)
        print(f"Minute {i}, EMA Recommendation: {buy_recommendation}, K-line Recommendation: {candle_recommendation}")

        if buy_recommendation == "STRONG_BUY" and holding_coin < MAX_HOLDING_COIN and candle_recommendation == K_LINE_STRONG_BUY:
            if holding_coin + 0.002 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.002
            account_balance, order_price = place_market_order(symbol, 'BUY', quantity, account_balance)
            print(f"Bought {quantity} of {symbol} at ${order_price}")
            holding_coin += quantity

        elif buy_recommendation == "BUY" and holding_coin < MAX_HOLDING_COIN and candle_recommendation == K_LINE_BUY:
            if holding_coin + 0.001 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.001
            account_balance, order_price = place_market_order(symbol, 'BUY', quantity, account_balance)
            print(f"Bought {quantity} of {symbol} at ${order_price}")
            holding_coin += quantity

        elif buy_recommendation == "SELL" and holding_coin > 0 and candle_recommendation == K_LINE_SELL:
            if holding_coin > 0.002:
                sell_amount = holding_coin * 0.5
            else:
                sell_amount = holding_coin
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
            print(f"Sold {quantity} of {symbol} at ${order_price}")
            holding_coin -= sell_amount

        elif buy_recommendation == "STRONG_SELL" and holding_coin > 0 and candle_recommendation == K_LINE_STRONG_SELL:
            sell_amount = holding_coin
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
            print(f"Sold {quantity} of {symbol} at ${order_price}")
            holding_coin -= sell_amount
            
        if holding_coin >= MAX_HOLDING_COIN:
            print(f"Max units of {symbol} has been reached at {holding_coin}")
        print('-----------------------------------------------------')
        time.sleep(60)
    final_sell(symbol, account_balance, holding_coin, starting_balance)


def main():
    symbol = 'BTCUSDT'
    minutes = 60
    candle_index = -5
    candle_initialisation = K_line_initialisation(candle_index)
    run_bot(minutes, symbol, 5000, 0.01, candle_index, candle_initialisation)


main()