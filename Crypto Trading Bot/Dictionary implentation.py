"""
Archer Simpson & Kodi Sinclair
30/9/24
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
# KODI'S KEYS
# API_KEY = 'rJljPrYroAaNOHIKfy0WJk2xWo9aeAjPsL5YSp2O6JQUTW8E5PU3aIz0hdeX7tO7'
# API_SECRET = 'aO0F2T3epauKW9GQGRj4Wlb8zxtCabFXHRE3e3f1nrgANl0FNTMCSkZYQfE6SzT3'


# ARCHERS KEY'S
API_KEY = 'QYHKtmBofXUNuHBJ352DG2jSAm9nz512wtDzteeKHvvGuFCXnJgw92xCbBiHJHfb'
API_SECRET = 'hSjOPnrSNzwZW592nhil2sBFpvEK24szznBOGIULGClSFfoNmDoOjfUNAYO2NPES'

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

recommendation_dict = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL':-2}

def print_all_available_coins():
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


def EMA_recommendation(symbol_for_anal):
    """
    Returns a bullish/bearish signal using EMA of varying lengths, calculated by trading_view_ta
    """
    coin = TA_Handler(
            symbol=symbol_for_anal,
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_MINUTE
        )
    analysis = coin.get_analysis()    

    # return recommendation_dict[analysis.moving_averages['RECOMMENDATION']]
    return recommendation_dict[analysis.moving_averages['COMPUTE']['Ichimoku']]
    # return analysis.moving_averages['COMPUTE']


def K_line_initialisation(candle_index, ticker):
    """
    The amount of Candles that it analyses must be an odd Integer
    Returns an integer representation of bullish/bearish signals based on the current market candles
    2 = Very Bullish 
    1 = Slightly Bullish
    -1 = Slightly Bearish 
    -2 = Very Bearish 
    """
    #Pulls K-line information from API 
    candles = client.get_klines(symbol = ticker, interval = client.KLINE_INTERVAL_1MINUTE)

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


def K_line_recommendation(signals, candle_index, ticker):
    #converting Bool signal into Integer representation 
    buy_signal_counter = 0 

    candles = client.get_klines(symbol = ticker, interval = client.KLINE_INTERVAL_1MINUTE)
    for signal in signals:
        if signal == True:
            buy_signal_counter += 1 
        else:
            buy_signal_counter -= 1 

    if buy_signal_counter < 0 and buy_signal_counter > (candle_index // 2):
        k_line_signal = recommendation_dict["SELL"]
    elif buy_signal_counter <= (candle_index // 2):
        k_line_signal = recommendation_dict["STRONG_SELL"]
    elif buy_signal_counter > 0 and buy_signal_counter < abs(candle_index // 2 ):
        k_line_signal = recommendation_dict["BUY"]
    else:
        k_line_signal = recommendation_dict["STRONG_BUY"]
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[candle_index]
    current_close = close_price
    open_time, open_price, high_price, low_price, close_price, volume, close_time, base_asset_volume, number_of_trades, executed_buy_volume, executed_buy_base_volume, ignore = candles[-1]
    signals.pop(0)
    if close_price > current_close:
        signals.append(True)
    else:
        signals.append(False)

    #return final recommendation
    return k_line_signal


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


def valid_order_amount(quantity, symbol):
    order_valid = False

    coin_details = client.get_symbol_info(symbol)['filters']
    lot_size_coin_details = coin_details[1]
    min_quantity = lot_size_coin_details['minQty']
    max_quantity = lot_size_coin_details['maxQty']
    if quantity > float(min_quantity) and quantity < float(max_quantity):
        lot_order_valid = True
    else:
        lot_order_valid = False

    notional_size_coin_details = coin_details[6]
    min_notional = notional_size_coin_details['minNotional']
    max_notional = notional_size_coin_details['maxNotional']
    average_price = client.get_avg_price(symbol=symbol)['price']
    notional_value = float(average_price) * quantity
    if notional_value > float(min_notional) and notional_value < float(max_notional):
        notional_order_valid = True
    else:
        notional_order_valid = False

    if notional_order_valid is True and lot_order_valid is True:
        order_valid = True

    return order_valid


def place_market_order(symbol, sell_or_buy, order_size, account_balance):
    """Places a market order"""
    # Changes the side parameter that will be used to place an order based on whether we want to sell or buy
    if sell_or_buy == 'BUY':
        side_type = SIDE_BUY
    elif sell_or_buy == 'SELL':
        side_type = SIDE_SELL
    # Rounds the buy quantity to the nearest step size to prevent crashing
    quantity = round_to_step_size(symbol, order_size)
    valid_quantity = valid_order_amount(quantity, symbol)
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
            print(f"Sold {sell_amount} of {symbol} at ${order_price}")
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


def run_bot(operating_mins, starting_symbol, starting_balance, max_holding, candle_index, candle_initialisation):
    symbol = starting_symbol
    MAX_HOLDING_VALUE = max_holding
    holding_coin = 0
    account_balance = starting_balance
    current_coin_prices = get_usdt_coins_prices()
    onehr_ago_coin_prices = None
    # This for loop will loop every minute
    for i in range(operating_mins):

        if (i % 60 == 0) and (i > 0):
            closing_balance = final_sell(symbol, account_balance, holding_coin, starting_balance)
            onehr_ago_coin_prices = current_coin_prices
            current_coin_prices = get_usdt_coins_prices()
            best_coin, onehour_percent_increase = greatest_price_increase(onehr_ago_coin_prices, current_coin_prices)
            symbol = best_coin
            print(f"Coin changing to: {symbol}. 1 Hour Price Change: {onehour_percent_increase:.2f}")
            holding_coin = 0
            account_balance = closing_balance

        current_price = get_current_price(symbol)
        holding_value = holding_coin * float(current_price)
        
        buy_recommendation = EMA_recommendation(symbol)
        candle_recommendation = K_line_recommendation(candle_initialisation, candle_index, symbol)

        print(f"Minute {i}, EMA Recommendation: {buy_recommendation}, K-line Recommendation: {candle_recommendation}")


        if buy_recommendation == 2 and holding_value < MAX_HOLDING_VALUE:

            if candle_recommendation == 2:
                # If both EMA and K-Line are showing STRONG_BUY signals, then the bot buys at 30% of max holdings
                buy_quantity_value = MAX_HOLDING_VALUE * 0.3
                coin_quantity = buy_quantity_value / float(get_current_price(symbol))
                account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
                if order_price != -1:
                    print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                    holding_coin += coin_quantity
                else:
                    print("Buy order is too small!")
                # The amount of coin that is being held with the newly bought coin
                

            elif candle_recommendation == 1:
                # If EMA is STRONG_BUY and K-Line is BUY, the bot buys at 20% of max holding
                buy_quantity_value = MAX_HOLDING_VALUE * 0.2
                coin_quantity = buy_quantity_value / float(get_current_price(symbol))
                account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
                if order_price != -1:
                    print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                    holding_coin += coin_quantity
                else:
                    print("Buy order is too small!")
                # The amount of coin that is being held with the newly bought coin
                


        elif buy_recommendation == 1 and holding_value < MAX_HOLDING_VALUE:
            
            if candle_recommendation == 2:
                 # If EMA is BUY and K-Line is STRONG_BUY, the bot buys at 20% of max holding
                buy_quantity_value = MAX_HOLDING_VALUE * 0.2
                coin_quantity = buy_quantity_value / float(get_current_price(symbol))
                account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
                if order_price != -1:
                    print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                    holding_coin += coin_quantity
                else:
                    print("Buy order is too small!")
                

            elif candle_recommendation == 1:
                # If both EMA and K-Line are showing BUY signals, then the bot buys at 10% of max holdings
                buy_quantity_value = MAX_HOLDING_VALUE * 0.1
                coin_quantity = buy_quantity_value / float(get_current_price(symbol))
                account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
                if order_price != -1:
                    print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                    holding_coin += coin_quantity
                else:
                    print("Buy order is too small!")
                


        elif buy_recommendation == -1 and holding_coin > 0:

            if candle_recommendation == -2 :
                # If EMA is SELL and K-Line is STRONG_SELL, the bot sells at 75% of max holding
                sell_amount = holding_coin * 0.75
                account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
                if order_price != -1:
                    print(f"Sold {sell_amount} of {symbol} at ${order_price}")
                    holding_coin -= sell_amount
                else:
                    print("Sell amount too small!")
                

            if candle_recommendation == -1:
                # If EMA is SELL and K-Line is also SELL, the bot sells at 50% of max holding
                sell_amount = holding_coin * 0.5
                account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
                if order_price != -1:
                    print(f"Sold {sell_amount} of {symbol} at ${order_price}")
                    holding_coin -= sell_amount
                else:
                    print("Sell amount too small!")




        elif buy_recommendation == -2 and holding_coin > 0:

            if candle_recommendation == -2:
                # If both EMA and K-Line are showing STRONG_SELL signals, then the bot sells all holdings
                sell_amount = holding_coin
                account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
                if order_price != -1:
                    print(f"Sold {sell_amount} of {symbol} at ${order_price}")
                    holding_coin -= sell_amount
                else:
                    print("Sell amount too small!")

            if candle_recommendation == -1:
                # If EMA is STRONG_SELL and K-Line is SELL, the bot sells at 75% of max holding
                sell_amount = holding_coin * 0.75
                account_balance, order_price = place_market_order(symbol, 'SELL', sell_amount, account_balance)
                if order_price != -1:
                    print(f"Sold {sell_amount} of {symbol} at ${order_price}")
                    holding_coin -= sell_amount
                else:
                    print("Sell amount too small!")
            

            
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
    symbol = 'USTCUSDT'
    minutes = 59
    candle_index = -3
    starting_balance = 5000
    max_holdings = 1000
    candle_initialisation = K_line_initialisation(candle_index, symbol)
    run_bot(minutes, symbol, starting_balance, max_holdings, candle_index, candle_initialisation)

 
main()
