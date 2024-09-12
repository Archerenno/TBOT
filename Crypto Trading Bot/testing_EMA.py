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

def account_info():
    info = client.get_account()
    return info

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

def get_order_price(symbol):
    trades = client.get_my_trades(symbol = symbol)
    return trades[-1]['price']

def final_sell(symbol, account_balance, holding_coin):
    sell_amount = holding_coin
    if sell_amount > 0:
        try:
            order = client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=sell_amount
            )
            sell_price = get_order_price(symbol)
            final_gain = float(sell_price) * sell_amount
            closing_balance = account_balance + final_gain
            print(f"Sold {sell_amount} of {symbol} at ${sell_price}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        closing_balance = account_balance
    print(f"Closing Account Balance: ${closing_balance}")
    print('-----------------------------------------------------')
    total_profit = closing_balance - 10000
    if total_profit >= 0:
        print(f"TOTAL PROFIT: ${total_profit}")
    else:
        print(f"TOTAL PROFIT: -${abs(total_profit)}")


def run_bot(operating_mins):
    symbol = 'BTCUSDT'
    holding_coin = 0
    account_balance = 5000
    for i in range(operating_mins):
        buy_price = get_order_price(symbol)
        print(f"Currently holding {holding_coin} units of Bitcoin, valued at ${buy_price} per unit")
        print(f"Account Balance: ${account_balance}")
        buy_recommendation = EMA_recommendation(i)
        if buy_recommendation == "STRONG_BUY" and holding_coin < 0.01:
            quantity = 0.002
            # Place a test market order
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                buy_price = get_order_price(symbol)
                account_balance -= float(buy_price) * quantity
                print(f"Bought {quantity} of {symbol} at ${buy_price}")
            except Exception as e:
                print(f"An error occurred: {e}")
            holding_coin += quantity
        elif buy_recommendation == "BUY" and holding_coin < 0.01:
            quantity = 0.001
            # Place a test market order
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                buy_price = get_order_price(symbol)
                account_balance -= float(buy_price) * quantity
                print(f"Bought {quantity} of {symbol} at ${buy_price}")
            except Exception as e:
                print(f"An error occurred: {e}")
            holding_coin += quantity
        elif buy_recommendation == "SELL" and holding_coin > 0:
            if holding_coin > 0.002:
                sell_amount = holding_coin * 0.5
            else:
                sell_amount = holding_coin
            # Place a test market order
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=sell_amount
                )
                sell_price = get_order_price(symbol)
                account_balance += float(sell_price) * sell_amount
                print(f"Sold {sell_amount} of {symbol} at ${buy_price}")
            except Exception as e:
                print(f"An error occurred: {e}")
            holding_coin -= sell_amount
        elif buy_recommendation == "STRONG_SELL" and holding_coin > 0:
            sell_amount = holding_coin
            try:
                order = client.create_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=sell_amount
                )
                sell_price = get_order_price(symbol)
                account_balance += float(sell_price) * sell_amount
                print(f"Sold {sell_amount} of {symbol} at ${sell_price}")
            except Exception as e:
                print(f"An error occurred: {e}")
            holding_coin -= sell_amount
        print('-----------------------------------------------------')
        time.sleep(60)
    final_sell(symbol, account_balance, holding_coin)


def main():
    minutes = 15
    run_bot(minutes)
    # account_balance = account_info()['balances'][4]['free']
    # print(f"Official API Account balance: ${float(account_balance):.2f}")
    # symbol = 'BTCUSDT'
    # min_buy_quantity = client.get_symbol_info(symbol)['filters'][1]
    # print(f"Coin: {symbol}")
    # print(f"Type: {min_buy_quantity['filterType']}")
    # print(f"    - Minimum Coin you can hold: {min_buy_quantity['minQty']}")
    # print(f"    - Max Coin you can hold: {min_buy_quantity['maxQty']}")
    # print(f"    - Step Size (Minimum order amount): {min_buy_quantity['stepSize']}")


main()
