# 📈 Binance Futures Trading Bot

A Python-based automated trading bot for Binance Futures that uses **Moving Averages (MA)** and **Relative Strength Index (RSI)** to generate buy/sell signals. It supports test mode operation and sends **email alerts** for each trade signal.

---

## 🚀 Features

- ✅ Fetches historical futures data from Binance
- 📊 Uses short/long Moving Averages & RSI for trade signals
- 📬 Sends email notifications on trade actions
- 🧪 Test mode support (no real trades)
- 🧾 Logs all activity to a file (`logs/futures_bot.log`)

---

## 📦 Requirements

- Python 3.7+
- Binance API key and secret
- Gmail account (for notifications)
- `.env` file with credentials

### 🐍 Install Python dependencies

```bash
pip install -r requirements.txt
```

#### requirements.txt example:
```txt
binance
pandas
requests
python-dotenv
termcolor
```
## 🔐 .env Configuration

#### Create a .env file in the root directory:
```env
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
EMAIL_SENDER=youremail@gmail.com
EMAIL_PASSWORD=your_email_app_password
EMAIL_RECEIVER=receiveremail@gmail.com
```
⚠️ Use an App Password for Gmail if 2FA is enabled.

## ⚙️ Configuration

#### Modify these in the script:
```python
TRADE_PAIRS = ['BTCUSDT', 'ETHUSDT']
TRADE_QUANTITY = 0.001
MA_SHORT_PERIOD = 5
MA_LONG_PERIOD = 20
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
is_test_mode = True
```
## ▶️ Running the Bot
```bash
python3 futures_trading_bot.py
```
## 📧 Example Email Alerts

-    Subject: Buy Signal

-    Message: Buy signal for BTCUSDT.

## 🧠 Strategy Logic

-    Buy: When short MA > long MA and RSI < oversold (30)

-    Sell: When short MA < long MA and RSI > overbought (70)

## 🧪 Test Mode

If is_test_mode = True, the bot simulates trades and logs them, but does not place real orders.

## 📁 Project Structure
```bash
.
├── .env
├── futures_trading_bot.py
├── logs/
│   └── futures_bot.log
├── requirements.txt
└── README.md
```
## 🛡️ Disclaimer

This bot is for educational and testing purposes only. Trading cryptocurrencies involves significant risk. Use at your own discretion.

## Official Channels

- [YouTube @rootctf](https://www.youtube.com/@rootctf)
- [X @r0otk3r](https://x.com/r0otk3r)
