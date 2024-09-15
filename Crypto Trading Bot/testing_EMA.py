"""
Archer Simpson
15/9/24
Trading Bot Project - Using a Binance Testnet
"""

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
import json
from binance.client import Client
from binance.enums import *
import time

# Testnet API credentials
# ARCHER'S KEYS
API_KEY = 'QYHKtmBofXUNuHBJ352DG2jSAm9nz512wtDzteeKHvvGuFCXnJgw92xCbBiHJHfb'
API_SECRET = 'hSjOPnrSNzwZW592nhil2sBFpvEK24szznBOGIULGClSFfoNmDoOjfUNAYO2NPES'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url


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


def run_bot(operating_mins, symbol, starting_balance, max_holding):
    MAX_HOLDING_COIN = max_holding
    holding_coin = 0
    account_balance = starting_balance
    for i in range(operating_mins):
        current_price = get_current_price(symbol)
        print(f"Currently holding {holding_coin} units of {symbol}, valued at ${float(current_price):.2f} per unit")
        print(f"Account Balance: ${account_balance}")
        buy_recommendation = EMA_recommendation()
        print(f"Minute {i}, EMA Recommendation: {buy_recommendation}")

        if buy_recommendation == "STRONG_BUY" and holding_coin < MAX_HOLDING_COIN:
            if holding_coin + 0.002 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.002
            account_balance, order_price = place_market_order(symbol, 'BUY', quantity)
            print(f"Bought {quantity} of {symbol} at ${order_price}")
            holding_coin += quantity

        elif buy_recommendation == "BUY" and holding_coin < MAX_HOLDING_COIN:
            if holding_coin + 0.001 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.001
            account_balance, order_price = place_market_order(symbol, 'BUY', quantity)
            print(f"Bought {quantity} of {symbol} at ${order_price}")
            holding_coin += quantity

        elif buy_recommendation == "SELL" and holding_coin > 0:
            if holding_coin > 0.002:
                sell_amount = holding_coin * 0.5
            else:
                sell_amount = holding_coin
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount)
            print(f"Sold {quantity} of {symbol} at ${order_price}")
            holding_coin -= sell_amount

        elif buy_recommendation == "STRONG_SELL" and holding_coin > 0:
            sell_amount = holding_coin
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount)
            print(f"Sold {quantity} of {symbol} at ${order_price}")
            holding_coin -= sell_amount
            
        if holding_coin >= MAX_HOLDING_COIN:
            print(f"Max units of {symbol} has been reached at {holding_coin}")
        print('-----------------------------------------------------')
        time.sleep(60)
    final_sell(symbol, account_balance, holding_coin, starting_balance)


def main():
    symbol = 'BTCUSDT'
    minutes = 5
    run_bot(minutes, symbol, 5000, 0.01)


main()
