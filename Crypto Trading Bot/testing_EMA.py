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
# ARCHER'S KEYS
API_KEY = 'QYHKtmBofXUNuHBJ352DG2jSAm9nz512wtDzteeKHvvGuFCXnJgw92xCbBiHJHfb'
API_SECRET = 'hSjOPnrSNzwZW592nhil2sBFpvEK24szznBOGIULGClSFfoNmDoOjfUNAYO2NPES'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

def print_testnet_account_balance():
    info = client.get_account()
    account_balance = info['balances'][4]['free']
    print(f"Official Testnet Account balance: ${float(account_balance):.2f}")


def EMA_recommendation(minute):
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
    print(f"Minute {minute}, EMA Recommendation: {analysis.moving_averages['RECOMMENDATION']}")
    return analysis.moving_averages['RECOMMENDATION']


def get_last_order_price(symbol):
    trades = client.get_my_trades(symbol = symbol)
    return trades[-1]['price']


def print_price(symbol, holding_coin):
    price_info = client.get_all_tickers()
    curr_price = price_info[3]['price']
    print(f"Currently holding {holding_coin} units of {symbol}, valued at ${float(curr_price):.2f} per unit")


def print_coin_information(symbol):
    min_buy_quantity = client.get_symbol_info(symbol)['filters'][1]
    print(f"Coin: {symbol}")
    print(f"Type: {min_buy_quantity['filterType']}")
    print(f"    - Minimum Coin you can hold: {min_buy_quantity['minQty']}")
    print(f"    - Max Coin you can hold: {min_buy_quantity['maxQty']}")
    print(f"    - Step Size (Minimum order amount): {min_buy_quantity['stepSize']}")


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
            print(f"{sell_or_buy} {order_size} of {symbol} at ${order_price}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return account_balance


def update_account_balance(sell_or_buy, order_price, order_size, account_balance):
    if sell_or_buy == 'SELL':
        account_balance += float(order_price) * order_size
    else:
        account_balance -= float(order_price) * order_size
    return account_balance


def print_trading_profit(closing_balance, starting_account_balance):
    total_profit = closing_balance - starting_account_balance
    if total_profit >= 0:
        print(f"TOTAL PROFIT: ${total_profit}")
    else:
        print(f"TOTAL PROFIT: -${abs(total_profit)}")


def final_sell(symbol, account_balance, holding_coin, starting_account_balance):
    sell_amount = holding_coin
    if sell_amount > 0:
        closing_balance = place_market_order(symbol, 'SELL', sell_amount)
    else:
        closing_balance = account_balance
    print(f"Closing Account Balance: ${closing_balance}")
    print('-----------------------------------------------------')
    print_trading_profit(closing_balance, starting_account_balance)


def run_bot(operating_mins, symbol, starting_balance, max_holding):
    MAX_HOLDING_COIN = max_holding
    holding_coin = 0
    account_balance = starting_balance
    for i in range(operating_mins):
        print_price(symbol, holding_coin)
        print(f"Account Balance: ${account_balance}")
        buy_recommendation = EMA_recommendation(i)
        if buy_recommendation == "STRONG_BUY" and holding_coin < MAX_HOLDING_COIN:
            if holding_coin + 0.002 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.002
            account_balance = place_market_order(symbol, 'BUY', quantity)
            holding_coin += quantity
        elif buy_recommendation == "BUY" and holding_coin < MAX_HOLDING_COIN:
            if holding_coin + 0.001 > MAX_HOLDING_COIN:
                quantity = 0.01 - holding_coin
            else:
                quantity = 0.001
            account_balance = place_market_order(symbol, 'BUY', quantity)
            holding_coin += quantity
        elif buy_recommendation == "SELL" and holding_coin > 0:
            if holding_coin > 0.002:
                sell_amount = holding_coin * 0.5
            else:
                sell_amount = holding_coin
            account_balance = place_market_order(symbol, 'SELL', sell_amount)
            holding_coin -= sell_amount
        elif buy_recommendation == "STRONG_SELL" and holding_coin > 0:
            sell_amount = holding_coin
            account_balance = place_market_order(symbol, 'SELL', sell_amount)
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