# TBOT

Current Version: 1.0

## Introduction:
TBOT is a trading bot specialising in cryptocurrencies which has been in development since August 2024. TBOT uses Binance and Trading View libraries to perform analysis on coins and then commits buy or sell orders depending on these signals. Additionally, the backtesting TBOT programs make use of the backtester library so that we can test the trading bots at faster than real time speeds.

## Files:
The most up to date file is 'Main TBOT'. This script runs on the Binance Testnet Server which is a server with live crypto prices that uses fake currency to test trading bots without risk. All MainNet (real money) scripts have developed outside of Github for security purposes. Ichimoku.py is an in-progress implementation of the ichimoku cloud technical indicator and the backtesting scripts use the backtrader libraries to test the model with live (trailing X hours) and historical market data

## Testing:
Extensive testing has been done on TBOT, mostly on the TestNet server but also on the MainNet with small, personal funds. We currently have over 45 hours of live testing completed on the Binance Testnet server and another 10 hours on MainNet. Testing is recorded on a spreadsheet.

## Updates:
TBOT is still in current development and some upcoming features we are actively working towards are:
- Ichimoku indicator
- Improving robustness of client-server connections
- Improving the logging capabilites of this function

### Contributors:
Trading Lead - Kodi Sinclair <br/>
Technical Lead - Archer Simpson
