"""
Archer Simpson & Kodi Sinclair
18/2/25
Trading Bot Project - Using a Binance Testnet
"""

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
from binance.client import Client
from binance.enums import *
import binance
import time
import numpy as np
import math
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_PUBLIC")
API_SECRET = os.getenv("API_PRIVATE")

# Base URL for Binance Testnet
testnet_url = 'https://testnet.binance.vision/api'

# Create a client instance for the testnet
client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = testnet_url

recommendation_dict = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL':-2}
# K_LINE_STRONG_BUY = 2
# K_LINE_BUY = 1 
# K_LINE_STRONG_SELL = -2 
# K_LINE_SELL = -1

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

    #NOTE DO WE WANT TO MODULARISE THE BELOW AS IT WILL BE OCCURING IN RSI AND MACD

    coin = TA_Handler(
            symbol=symbol_for_anal,
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_MINUTE
        )
    analysis = coin.get_analysis()    

    ema20 = analysis.moving_averages['COMPUTE']['EMA20']
    ema30 = analysis.moving_averages['COMPUTE']['EMA30']
    vwma = analysis.moving_averages['COMPUTE']['VWMA']
    ema_list = [ema20, ema30, vwma]
    ema_signal = compute_ema_from_indicators(ema_list)
    print(f"EMA Signal: {recommendation_dict[ema_signal]}")
    return recommendation_dict[ema_signal]


def compute_ema_from_indicators(ema_list):
    signal = 0
    for ema in ema_list:
        if ema == "BUY":
            signal += 1
        elif ema == "SELL":
            signal -= 1
    if signal == 3:
        return "STRONG_BUY"
    elif signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    elif signal == -3:
        return "STRONG_SELL"



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
    print(f"K-Line Signal: {k_line_signal}")
    return k_line_signal




def RSI(symbol_for_anal):
    """gets the RSI value and returns 'STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL', 'NEUTRAL' """
    
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

    if RSI_value <= 30:
        RSI_signal = recommendation_dict["BUY"]

    elif RSI_value >= 70:
        RSI_signal = recommendation_dict["SELL"]
    
    else:
        RSI_signal = recommendation_dict["NEUTRAL"]
    print(f"RSI Signal: {RSI_signal}")
    return RSI_signal



def MACD(symbol_for_anal):
    coin = TA_Handler(
            symbol=symbol_for_anal,
            screener="crypto",
            exchange="BINANCE",
            interval=Interval.INTERVAL_1_MINUTE
        )
    
    analysis = coin.get_analysis()

    curr_macd_macd = analysis.indicators["MACD.macd"]
    curr_macd_signal = analysis.indicators["MACD.signal"]

    return curr_macd_macd, curr_macd_signal
    


def MACD_analysis(curr_macd_macd, curr_macd_signal, prev_macd_macd, prev_macd_signal):
    """Going to continuously look at and see if cross over occurs but will only give 'BUY' or 'SELL' signals  """

    if prev_macd_macd < prev_macd_signal:
        prev_signal_above = True
    else:
        prev_signal_above = False


    if curr_macd_macd < curr_macd_signal:
        curr_signal_above = True
    else:
        curr_signal_above = False

    if prev_signal_above is True and curr_signal_above is False:
        return recommendation_dict["BUY"]
    elif prev_signal_above is False and curr_signal_above is True:
        return recommendation_dict["SELL"]
    


    return recommendation_dict["NEUTRAL"]


def frequent_analysis(symbol, k_line_list):

    buy_recommendation = EMA_recommendation(symbol)
    candle_recommendation = K_line_recommendation(k_line_list[1], k_line_list[0], symbol)

    frequent_recommendation = math.ceil((buy_recommendation + candle_recommendation) / 2 )

    return frequent_recommendation

def infrequent_analysis(symbol, MACD_recommendaiton):

    RSI_recommendation = RSI(symbol)
    infrequent_recommendation = (0.5 * MACD_recommendaiton + 0.5 * RSI_recommendation) * 2

    return infrequent_recommendation

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
    #NOTE: Unproven that this code even works
    price_change_percent = ((final - initial)/ initial) * 100        
    max_increase_index = np.argmax(price_change_percent)
    greatest_percent_value = price_change_percent[max_increase_index]
    usdt_coins = get_usdt_coin_symbols()
    greatest_percent_coin = usdt_coins[max_increase_index]
    past_day_kline = client.get_klines(symbol = greatest_percent_coin, interval = client.KLINE_INTERVAL_1DAY)
    while past_day_kline == 1:
        print(f"{greatest_percent_coin} is not old enough to be traded, attempting to change coin again")
        price_change_percent = np.delete(price_change_percent, max_increase_index)
        max_increase_index = np.argmax(price_change_percent)
        greatest_percent_value = price_change_percent[max_increase_index]
        greatest_percent_coin = usdt_coins[max_increase_index]
        past_day_kline = client.get_klines(symbol = greatest_percent_coin, interval = client.KLINE_INTERVAL_1DAY)
    return (greatest_percent_coin, greatest_percent_value)


def combined_analysis(symbol, MACD_recommendation, k_line_list):
    frequent_signal = frequent_analysis(symbol, k_line_list)
    infrequent_signal = infrequent_analysis(symbol, MACD_recommendation)
    if infrequent_signal == 0:
        weighted_signal = frequent_signal
    else:
        weighted_signal = 0.25 * frequent_signal + 0.75 * infrequent_signal
    return weighted_signal


def final_buy_signal(symbol, MACD_recommendation, k_line_list):
    # Returns a value between -2 and 2, which can take on linear combinations of 0.35 and 0.65
    combined_buy_signal = combined_analysis(symbol, MACD_recommendation ,k_line_list)
    buy_amount = (5 * combined_buy_signal)/10

    #NOTE TESTING PRINT 
    print(f"Final buy signal = {combined_buy_signal}")
    return buy_amount

def get_holding_coin(symbol):
    curr_holding = client.get_asset_balance(asset = symbol)
    return curr_holding['free']

def initialise_file():
    """ Initialises the file when the code is first ran. """
    time_str = str(time.ctime())
    curr_day = time_str[0:11]
    curr_year = time_str[-4:]
    curr_date = curr_day + curr_year
    folder_path = 'Crypto Trading Bot/testRecord'
    file_path = os.path.join(folder_path, f"{curr_date}.txt")
    with open(file_path, "w") as file: 
        file.writelines("COIN, ACTION, PRICE, QUANTITY, TIMESTAMP, EMA, K-LINE, RSI, MACD ")
    return file_path, time_str

def trade_history_storage(file_path, time_str, order_info):
    """ is called upon each time a buy / sell trade is executed. """

    with open(file_path, "w") as file:
        file.write(f"{order_info['COIN']}, {order_info['ACTION']}, {order_info['PRICE']}, {order_info['QUANTITY']}, {time_str}, {order_info['EMA']}, {order_info['K-LINE']}, {order_info['K-LINE']}, {order_info['RSI']}, {order_info['MACD']} \n")


def run_bot(operating_mins, starting_symbol, starting_balance, max_holding, k_line_list):
    symbol = starting_symbol
    MAX_HOLDING_VALUE = max_holding
    holding_coin = 0
    account_balance = starting_balance

    file_path, time_str = initialise_file()
    current_coin_prices = get_usdt_coins_prices()
    onehr_ago_coin_prices = None
    # This for loop will loop every minute

    prev_MACD_anal = []

    for i in range(operating_mins):
        print(f"Minute {i}")
        if (i % 60 == 0) and (i > 0):
            onehr_ago_coin_prices = current_coin_prices
            current_coin_prices = get_usdt_coins_prices()
            best_coin, onehour_percent_increase = greatest_price_increase(onehr_ago_coin_prices, current_coin_prices)
            if best_coin != symbol:
                closing_balance = final_sell(symbol, account_balance, holding_coin, starting_balance)
                print(f"Coin changing to: {best_coin}. \n 1 Hour Price Change: {onehour_percent_increase:.2f}")
                symbol = best_coin
                holding_coin = 0
                account_balance = closing_balance
            else:
                print(f"Top peforming coin is still {symbol}")

        if i == 0:
            prev_macd_macd, prev_macd_signal = MACD(symbol)
            MACD_recommendation = recommendation_dict["NEUTRAL"]
            print("initialising MACD Values")
        elif i == 1 :
            curr_macd_macd, curr_macd_signal = MACD(symbol)
            MACD_recommendation = recommendation_dict["NEUTRAL"]
            print("Initialising MACD Values")
        else:
            prev_macd_macd = curr_macd_macd
            prev_macd_signal = curr_macd_signal
            curr_macd_macd, curr_macd_signal = MACD(symbol)
            MACD_recommendation = MACD_analysis(curr_macd_macd, curr_macd_signal, prev_macd_macd, prev_macd_signal)
            prev_MACD_anal.append(MACD_recommendation)
            print(f"MACD Signal: {MACD_recommendation}")

        current_price = get_current_price(symbol)

        holding_value = holding_coin * float(current_price)
        
        order_percent = final_buy_signal(symbol, MACD_recommendation, k_line_list)


        if order_percent > 0 and holding_value < MAX_HOLDING_VALUE:
            buy_quantity = order_percent * MAX_HOLDING_VALUE
            coin_quantity = buy_quantity / float(get_current_price(symbol))
            account_balance, order_price = place_market_order(symbol, 'BUY', coin_quantity, account_balance)
            if order_price != -1:
                print(f"Bought {coin_quantity} of {symbol} at ${order_price}")
                holding_coin += coin_quantity
                order_info = {'COIN' : symbol, 'ACTION' : 'BUY', 'PRICE' : order_price, 'QUANTITY' : buy_quantity ,'EMA': EMA_signal, 'K-LINE' : candle_recommendation, 'RSI' : RSI_recommendation, "MACD" : MACD_recommendation }
                trade_history_storage(file_path, time_str, order_info)
            else:
                print("Buy order is too small!")
                # The amount of coin that is being held with the newly bought coin
        
        elif order_percent < 0 and holding_value > 0:
            sell_quantity = abs(order_percent * holding_coin)
            account_balance, order_price = place_market_order(symbol, 'SELL', sell_quantity, account_balance)
            if order_price != -1:
                print(f"Sold {sell_quantity} of {symbol} at ${order_price}")
                holding_coin -= sell_quantity
                order_info = {'COIN' : symbol, 'ACTION' : 'SELL', 'PRICE' : order_price, 'QUANTITY' : buy_quantity ,'EMA': EMA_signal, 'K-LINE' : candle_recommendation, 'RSI' : RSI_recommendation, "MACD" : MACD_recommendation }
                trade_history_storage(file_path, time_str, order_info)
            else:
                print("Sell amount too small!")

        else:
            pass
       
        holding_value = holding_coin * float(current_price)

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
    symbol = 'PEPEUSDT'
    minutes = 59
    candle_index = -3
    starting_balance = 5000
    max_holdings = 1000
    candle_initialisation = K_line_initialisation(candle_index, symbol)
    k_line_list = [candle_index, candle_initialisation]
    

    run_bot(minutes, symbol, starting_balance, max_holdings, k_line_list)
    # final_sell(symbol, 4800, 310.4, 5000)

main()

