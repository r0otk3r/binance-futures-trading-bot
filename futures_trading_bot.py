#!/usr/bin/env python3
#By r0otk3r

import time
import logging
import requests
import pandas as pd
from binance.client import Client
from binance.enums import *
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from termcolor import colored
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Setting up logging to capture the bot's activities
logging.basicConfig(filename='logs/futures_bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Binance API Keys (stored securely using environment variables)
API_KEY = os.getenv('')
API_SECRET = os.getenv('')

# Initialize Binance Client for market data and order placement
client = Client(API_KEY, API_SECRET)

# Define the trading pairs (assets to trade), quantity, and moving average settings
TRADE_PAIRS = ['BTCUSDT', 'ETHUSDT']  # Example trading pairs for the bot
TRADE_QUANTITY = 0.001  # Set trade quantity for each order
MA_SHORT_PERIOD = 5  # Short period for moving average
MA_LONG_PERIOD = 20  # Long period for moving average
RSI_PERIOD = 14  # Period for RSI (Relative Strength Index)
RSI_OVERBOUGHT = 70  # RSI level for overbought condition
RSI_OVERSOLD = 30  # RSI level for oversold condition

# Email Notification settings for alerting on trades
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('')
EMAIL_RECEIVER = os.getenv('')

# Test Mode Flag - Set to True for test mode (no actual trades placed)
is_test_mode = True

# Function to send email notifications for buy/sell signals
def send_email_notification(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        logging.info("Email notification sent successfully.")
        print(colored("Email notification sent successfully.", 'green'))
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        print(colored(f"Error sending email: {str(e)}", 'red'))

# Function to fetch historical market data (candlestick data) from Binance
def fetch_historical_data(pair, interval='1m', limit=100):
    try:
        logging.info(f"Fetching historical data for {pair}...")
        
        # Calculate the start time based on the interval and limit
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=limit if interval == '1m' else limit * 60)
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

        # Fetch historical klines
        klines = client.futures_historical_klines(pair, interval, start_str)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)
        df.set_index('timestamp', inplace=True)
        logging.info(f"Fetched {len(df)} data points for {pair}.")
        return df
    except BinanceAPIException as e:
        logging.error(f"Error fetching data for {pair}: {e.message}")
        print(colored(f"Error fetching data for {pair}: {e.message}", 'red'))
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(colored(f"Unexpected error: {str(e)}", 'red'))
        return None

# Function to calculate moving averages (both short-term and long-term)
def calculate_moving_average(data, period):
    return data['close'].rolling(window=period).mean()

# Function to calculate RSI (Relative Strength Index)
def calculate_rsi(data, period):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Function to check if a buy signal is triggered based on moving averages and RSI
def check_buy_signal(df):
    short_ma = calculate_moving_average(df, MA_SHORT_PERIOD)
    long_ma = calculate_moving_average(df, MA_LONG_PERIOD)
    rsi = calculate_rsi(df, RSI_PERIOD)
    if short_ma.iloc[-1] > long_ma.iloc[-1] and rsi.iloc[-1] < RSI_OVERSOLD:
        return True
    return False

# Function to check if a sell signal is triggered based on moving averages and RSI
def check_sell_signal(df):
    short_ma = calculate_moving_average(df, MA_SHORT_PERIOD)
    long_ma = calculate_moving_average(df, MA_LONG_PERIOD)
    rsi = calculate_rsi(df, RSI_PERIOD)
    if short_ma.iloc[-1] < long_ma.iloc[-1] and rsi.iloc[-1] > RSI_OVERBOUGHT:
        return True
    return False

# Function to place a buy or sell order on Binance
def place_order(pair, side):
    try:
        if is_test_mode:
            logging.info(f"[TEST MODE] {side} order on {pair}.")
            print(colored(f"[TEST MODE] {side} order on {pair}.", 'yellow'))
        else:
            if side == 'BUY':
                order = client.futures_create_order(symbol=pair, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=TRADE_QUANTITY)
            else:
                order = client.futures_create_order(symbol=pair, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=TRADE_QUANTITY)
            logging.info(f"Order executed: {order}")
            print(colored(f"Order executed: {order}", 'blue'))
    except Exception as e:
        logging.error(f"Error placing order: {str(e)}")
        print(colored(f"Error placing order: {str(e)}", 'red'))

# Main bot function that checks market conditions and executes trades
def run_bot():
    print(colored("Starting Binance Futures Testnet trading bot...", 'blue'))
    logging.info("Binance Futures Testnet trading bot started.")

    while True:
        for pair in TRADE_PAIRS:
            df = fetch_historical_data(pair)
            if df is None:
                logging.error(f"Error with data for {pair}. Retrying...")
                time.sleep(60)
                continue

            if check_buy_signal(df):
                logging.info(f"Buy signal for {pair}.")
                print(colored(f"Buy signal for {pair}.", 'green'))
                send_email_notification("Buy Signal", f"Buy signal for {pair}.")
                place_order(pair, 'BUY')

            elif check_sell_signal(df):
                logging.info(f"Sell signal for {pair}.")
                print(colored(f"Sell signal for {pair}.", 'red'))
                send_email_notification("Sell Signal", f"Sell signal for {pair}.")
                place_order(pair, 'SELL')

        time.sleep(60)

# Run the trading bot
if __name__ == "__main__":
    run_bot()
