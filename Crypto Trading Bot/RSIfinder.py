"""
Archer Simpson
26/5/25
Trading Bot Project
"""

from tradingview_ta import TA_Handler, Interval, Exchange
from binance.client import Client
from binance.enums import *
import binance
import time
import numpy as np


recommendation_dict = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL':-2}

# ARCHERS KEY'S
API_KEY = 'QYHKtmBofXUNuHBJ352DG2jSAm9nz512wtDzteeKHvvGuFCXnJgw92xCbBiHJHfb'
API_SECRET = 'hSjOPnrSNzwZW592nhil2sBFpvEK24szznBOGIULGClSFfoNmDoOjfUNAYO2NPES'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

def print_all_available_coins():
    """Prints the tickers of all available coins through the Binance Exchange."""
    info = client.get_account()
    all_balances = info['balances']
    print("This is a list of all the available coins through Binance")
    print(all_balances)
    for coin in all_balances:
        print(coin['asset'])


def print_asset_account_balance(symbol):
    """Prints the account balance (this is different from the balance printed in the run bot loop) 
       NOTE: Must be in form 'BTC' or 'ETH", 3 letter identifier"""
    info = client.get_account()
    all_balances = info['balances']
    if symbol != "USDT":
        short_symbol = get_short_symbol(symbol)
    else:
        short_symbol = "USDT"
    # This for loop searches all of the balances for every symbol until it finds the one specified
    for coin in all_balances:
        if coin['asset'] == short_symbol:
            # The 'free' key in the dictionary says how much of the coin/currency you have available to use/spend
            account_balance = coin['free']
    print(f"Account balance ({symbol}): {float(account_balance):.4f}")


def get_curr_asset_balance(symbol):
    """Returns the account balance (this is different from the balance printed in the run bot loop) 
       NOTE: Must be in form 'BTC' or 'ETH", 3 letter identifier"""
    account_balance = None
    info = client.get_account()
    all_balances = info['balances']
    # This for loop searches all of the balances for every symbol until it finds the one specified
    for coin in all_balances:
        if coin['asset'] == symbol:
            # The 'free' key in the dictionary says how much of the coin/currency you have available to use/spend
            account_balance = coin['free']
    if account_balance is None:
        print(f"{symbol} does not exist on the binance exchange")
        return None
    else:
        return float(account_balance)


def print_coin_information(symbol):
    """NOTE: Only works for LOT_SIZE"""
    # The indexing of [1] at the end of the statement below is section that specifies the filertype LOT_SIZE.
    # Change this indexing if you want other filter types
    coin_info = client.get_symbol_info(symbol)['filters']
    lot_coin_info = coin_info[1]
    print(f"Coin: {symbol}")
    print(f"Type: {lot_coin_info['filterType']}")
    print(f"    - Minimum Coin you can hold: {lot_coin_info['minQty']}")
    print(f"    - Max Coin you can hold: {lot_coin_info['maxQty']}")
    print(f"    - Step Size (Minimum order amount): {lot_coin_info['stepSize']}")

    notional_coin_info = coin_info[6]
    print(f"Type: {notional_coin_info['filterType']}")
    print(f"    - Minimum order value: {notional_coin_info['minNotional']}")
    print(f"    - Max order value: {notional_coin_info['maxNotional']}")
    print(f"    - Average price over X minutes used to find notional: {notional_coin_info['avgPriceMins']}")


def RSI(symbol_for_anal):
    """gets the RSI value and returns 'STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL', 'NEUTRAL' as their respective integer representation """
    
    # Initialises RSI value to Neutral
    RSI_signal = recommendation_dict["NEUTRAL"]

    coin = TA_Handler(
            symbol=symbol_for_anal,
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_MINUTE
        )
    
    analysis = coin.get_analysis()   
    RSI_value =  analysis.indicators["RSI"]

    if RSI_value <= 31:
        RSI_signal = recommendation_dict["BUY"]

    elif RSI_value >= 75:
        RSI_signal = recommendation_dict["SELL"]

    print(f"RSI Signal: {RSI_value:.2f}")
    return RSI_signal


def get_last_order_price(symbol):
    """Get the coin price from the last order placed. Returns a string"""
    trades = client.get_my_trades(symbol = symbol)
    return trades[-1]['price']


def get_current_price(symbol):
    """Get the current price of the coin at the time function is called. Returns a string"""
    price_info = client.get_all_tickers()
    for coin in price_info:
        if coin['symbol'] == symbol:
            curr_price = coin['price']
    return curr_price


def round_to_step_size(symbol, amount):
    """
    Rounds the coin buy amount to the number of decimal places associated with the step size. This prevents the accuracy of the buy
    amount from getting so small that it causes a crash
    """
    # Index [1] here just refers to LOT_SIZE filter_type
    stepsize = client.get_symbol_info(symbol)['filters'][1]['stepSize']
    rounded_amount = binance.helpers.round_step_size(amount, stepsize)
    return rounded_amount


def valid_order_amount(quantity, symbol, sell_or_buy):
    order_valid = False

    coin_details = client.get_symbol_info(symbol)['filters']
    lot_size_coin_details = coin_details[3]
    min_quantity = lot_size_coin_details['minQty']
    max_quantity = lot_size_coin_details['maxQty']
    if quantity > float(min_quantity) and quantity < float(max_quantity):
        lot_order_valid = True
    else:
        lot_order_valid = False

    notional_size_coin_details = coin_details[6]
    min_notional = notional_size_coin_details['minNotional']
    max_notional = notional_size_coin_details['maxNotional']
    ticker_prices = client.get_orderbook_ticker(symbol=symbol)
    if sell_or_buy == "BUY":
        curr_price = ticker_prices["askPrice"]
    else:
        curr_price = ticker_prices["bidPrice"]
    notional_value = float(curr_price) * quantity
    if notional_value > float(min_notional) and notional_value < float(max_notional):
        notional_order_valid = True
    else:
        notional_order_valid = False

    if notional_order_valid is True and lot_order_valid is True:
        order_valid = True

    return order_valid


def get_short_symbol(symbol):
    """Takes in a symbol like BTCUSDT and removes the USDT part, leaving us with just BTC"""
    usdt_pos_in_string = symbol.find("USDT")
    short_symbol = symbol[:usdt_pos_in_string]
    return short_symbol


def place_market_order(symbol, sell_or_buy, order_size, account_balance):
    """Places a market order"""
    # Changes the side parameter that will be used to place an order based on whether we want to sell or buy
    if sell_or_buy == 'BUY':
        side_type = SIDE_BUY
    elif sell_or_buy == 'SELL':
        side_type = SIDE_SELL
    # Factors in the 0.1% commission on Binance exchange, made 0.2% for the sake of a buffer
    minus_commission = order_size * 0.998
    # Rounds the buy quantity to the nearest step size so that accuracy is not too great for API to handle
    quantity = round_to_step_size(symbol, minus_commission)
    valid_quantity = valid_order_amount(quantity, symbol, sell_or_buy)
    if valid_quantity is True:
        try:
                order = client.create_order(
                    symbol=symbol,
                    side=side_type,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
                order_price = get_last_order_price(symbol)
                account_balance = update_account_balance(sell_or_buy, order_price, quantity, account_balance)
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("ORDER FAILED: Order amount is invalid")
        order_price = -1
    return account_balance, order_price


def update_account_balance(sell_or_buy, order_price, order_size, account_balance):
    """Updates the account balance (the one that is displayed during run-time)"""
    if sell_or_buy == 'SELL':
        account_balance += float(order_price) * order_size
    else:
        account_balance -= float(order_price) * order_size
    return account_balance


def calculate_trading_profit(closing_balance, starting_account_balance):
    """Calculates the profit made after the bot has been run for the specified time"""
    total_profit = closing_balance - starting_account_balance
    if total_profit >= 0:
        return f"TOTAL PROFIT: ${total_profit}"
    else:
        return f"TOTAL PROFIT: -${abs(total_profit)}"


def final_sell(symbol, account_balance, holding_coin, starting_account_balance):
    """Once the run timer on the bot hits zero, all currently held coin is sold so that the total profit can then be calculated"""
    sell_amount = holding_coin
    # If coin is still being held at the end of the run-time sell everything and update the account balance
    if sell_amount > 0:
        closing_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
        if order_price != -1:
            print(f"Sold {sell_amount * 0.998} of {symbol} at ${order_price}")
        else:
            print("Not enough remaining balance to sell!")
    else:
        closing_balance = account_balance
    print(f"Closing Account Balance: ${closing_balance}")
    print("\n")
    print('------------------------------------------------------------------------')
    print("\n")
    profit_str = calculate_trading_profit(closing_balance, starting_account_balance)
    print(profit_str)
    return closing_balance



def get_holding_coin(symbol):
    curr_holding = client.get_asset_balance(asset = symbol)
    return curr_holding['free']



def find_coin():
    coin_found = False
    ticker_stats = client.get_all_tickers()
    usdt_only = [ticker for ticker in ticker_stats if ticker['symbol'].endswith('USDT')]
    sorted_by_price = sorted(usdt_only, key=lambda p:float(p['price']), reverse=True)
    for ticker in sorted_by_price:
        if RSI(ticker['symbol']) == 1:
            print(f"Coin chose: {ticker}")
            coin_found = True
            return True, ticker['symbol']
    if coin_found is False:
        print(f"No coin is currently a good buy according to the RSI finder")
        return False, None
        


def run_bot(operating_mins, starting_symbol, starting_balance, max_holding):
    symbol = starting_symbol
    MAX_HOLDING_VALUE = max_holding
    holding_coin = 0
    position = False
    account_balance = starting_balance

    print_asset_account_balance("USDT")
    print_asset_account_balance(symbol)
    # This for loop will loop every minute


    for i in range(operating_mins):
        print(f"Minute {i}")

        current_price = get_current_price(symbol)
        holding_coin = get_curr_asset_balance(get_short_symbol(symbol))

        holding_value = holding_coin * float(current_price)

        if holding_value < 0.9 * starting_balance:
            print("Current loss greater than 10%, selling all assets")
            final_sell(symbol, account_balance, holding_coin, starting_balance)
            return

        rsi = RSI(symbol)

        if position is False and rsi == 1:
            buy_quantity = MAX_HOLDING_VALUE
            coin_quantity = buy_quantity / float(get_current_price(symbol))
            account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
            if order_price != -1:
                print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                holding_coin += coin_quantity
                position = True
            else:
                print("Buy order is too small!")
                # The amount of coin that is being held with the newly bought coin
        
        elif position is True and rsi == -1:
            sell_quantity = holding_coin
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_quantity, account_balance)
            if order_price != -1:
                print(f"Sold {sell_quantity} of {symbol} at ${order_price}")
                holding_coin -= sell_quantity
                position = False
            else:
                print("Sell amount too small!")
                position = False

        elif position is False and rsi == -1:
            print("rsi is high & no current position. Switching coins")
            symbol = find_coin()
            position = False
       
            
        if holding_value >= MAX_HOLDING_VALUE:
            print(f"Max units of {symbol} has been reached at {holding_coin}. Currently valued at ${float(current_price)} per unit")
        else:
            print(f"Currently holding {holding_coin} units of {symbol}, valued at ${float(current_price)} per unit")
        print(f"Account Balance: ${account_balance}")
        print("\n")
        print('------------------------------------------------------------------------')
        print("\n")
        # The purpose of this sleep statement is to wait until new data is available through the API which is after 60 seconds
        time.sleep(60)
    # Sell all remaining coins at the end of the time period
    final_sell(symbol, account_balance, holding_coin, starting_balance)


def main():
    symbol = find_coin()
    if symbol[0] is True:
        minutes = 5
        starting_balance = get_curr_asset_balance('USDT')
        max_holdings = starting_balance
        run_bot(minutes, symbol[1], starting_balance, max_holdings)
    else:
        print("No coin found under RSI value at this moment")


main()
# find_coin()