"""
Archer Simpson
24/9/24
Trading Bot Project - Using a Binance Testnet
"""

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
from binance.client import Client
from binance.enums import *
import binance
import time
import numpy as np

# Testnet API credentials
# ARCHERS'S KEYS
API_KEY = 'QYHKtmBofXUNuHBJ352DG2jSAm9nz512wtDzteeKHvvGuFCXnJgw92xCbBiHJHfb'
API_SECRET = 'hSjOPnrSNzwZW592nhil2sBFpvEK24szznBOGIULGClSFfoNmDoOjfUNAYO2NPES'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url


def print_all_available_assets():
    """Prints the tickers of all available coins through the Binance Exchange."""
    info = client.get_account()
    all_balances = info['balances']
    print("This is a list of all the available coins through Binance")
    for coin in all_balances:
        print(coin['asset'])


def print_testnet_account_balance(symbol):
    """Prints the testnet account balance (this is different from the balance printed in the run bot loop)"""
    info = client.get_account()
    all_balances = info['balances']
    # This for loop searches all of the balances for every symbol until it finds the one specified
    for coin in all_balances:
        if coin['asset'] == symbol:
            # The 'free' key in the dictionary says how much of the coin/currency you have available to use/spend
            account_balance = coin['free']
    print(f"Official Testnet Account balance ({symbol}): {float(account_balance):.4f}")


def print_coin_information(symbol):
    """NOTE: Only works for LOT_SIZE"""
    # The indexing of [1] at the end of the statement below is section that specifies the filertype LOT_SIZE.
    # Change this indexing if you want other filter types
    coin_info = client.get_symbol_info(symbol)['filters'][1]
    print(f"Coin: {symbol}")
    print(f"Type: {coin_info['filterType']}")
    print(f"    - Minimum Coin you can hold: {coin_info['minQty']}")
    print(f"    - Max Coin you can hold: {coin_info['maxQty']}")
    print(f"    - Step Size (Minimum order amount): {coin_info['stepSize']}")


def get_usdt_coins_prices():
    coins = client.get_all_tickers()
    usdt_coins = [float(coin['price']) for coin in coins if coin['symbol'].endswith('USDT')]
    array_usdt_coins = np.array(usdt_coins)
    return array_usdt_coins

def get_usdt_coin_symbols():
    coins = client.get_all_tickers() 
    usdt_coins = [coin['symbol'] for coin in coins if coin['symbol'].endswith('USDT')]
    return usdt_coins

def greatest_price_increase(initial, final):
    price_change_percent = ((final - initial)/ initial) * 100
    max_increase_index = np.argmax(price_change_percent)
    greatest_percent_value = price_change_percent[max_increase_index]
    usdt_coins = get_usdt_coin_symbols()
    greatest_percent_coin = usdt_coins[max_increase_index]
    return (greatest_percent_coin, greatest_percent_value)


def main():
    price1 = get_usdt_coins_prices()
    time.sleep(60)
    price2 = get_usdt_coins_prices()
    print(greatest_price_increase(price1, price2))
    


main()
