
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 🔹 API Keys (Kept in the same file for Google Colab)
ALPHA_VANTAGE_API_KEY = "6VVQB7QEX6PWX0G6"
GOOGLE_FINANCE_API_KEY = "your_google_finance_api_key"
MARKETSTACK_API_KEY = "your_marketstack_api_key"

# 🔹 API Base URLs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
GOOGLE_FINANCE_BASE_URL = "https://serpapi.com/search"
MARKETSTACK_BASE_URL = "https://api.marketstack.com/v1"

# Function to fetch intraday stock data from Alpha Vantage
def get_intraday_stock_data(symbol):
    url = f"{ALPHA_VANTAGE_BASE_URL}?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()
    return data.get("Time Series (5min)", {})

# Function to fetch market movers (MarketStack)
def get_market_movers():
    market_url = f"{MARKETSTACK_BASE_URL}/tickers?access_key={MARKETSTACK_API_KEY}"
    response = requests.get(market_url)
    market_data = response.json()
    return market_data.get('data', [])

# Function to fetch ETF profile from Alpha Vantage
def get_etf_profile(symbol):
    etf_url = f"{ALPHA_VANTAGE_BASE_URL}?function=ETF_PROFILE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    etf_response = requests.get(etf_url)
    return etf_response.json()

# Function to fetch annual reports
def get_annual_reports(symbol):
    url = f"{ALPHA_VANTAGE_BASE_URL}?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    results = response.json()
    annual_reports = results.get('annualReports', [])

    if not annual_reports:
        return None

    report_dfs = [pd.DataFrame(report, index=[0]) for report in annual_reports]
    final_df = pd.concat(report_dfs, ignore_index=True) if report_dfs else None

    if final_df is not None:
        final_df.to_csv('combined_reports.csv', index=False)

    return final_df

# Function to calculate RSI
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate Moving Averages (SMA & EMA)
def calculate_moving_averages(prices, short_window=20, long_window=50):
    prices['SMA_20'] = prices['close'].rolling(window=short_window).mean()
    prices['EMA_50'] = prices['close'].ewm(span=long_window, adjust=False).mean()
    return prices

# Function to calculate VWAP
def calculate_vwap(df):
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df

# User Input
symbol = input("Enter a stock ticker: ").upper()

# Fetch Data
intraday_data = get_intraday_stock_data(symbol)
market_movers = get_market_movers()
etf_profile = get_etf_profile(symbol)
annual_report_df = get_annual_reports(symbol)

# Convert intraday data to DataFrame
df = pd.DataFrame.from_dict(intraday_data, orient='index')
df = df.astype(float)
df.index = pd.to_datetime(df.index)
df = df.sort_index()  # Ensure time is in ascending order
df = df.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. volume': 'volume'})

# Compute Technical Indicators
df = calculate_moving_averages(df)
df['RSI_14'] = calculate_rsi(df['close'])
df = calculate_vwap(df)

# Save Processed Data
df.to_csv(f"{symbol}_stock_analysis.csv", index=True)

# Display Outputs
print("\nIntraday Stock Data:")
print(df.tail())

print("\nETF Profile Data:")
print(etf_profile)

print("\nAnnual Reports (Saved to CSV):")
if annual_report_df is not None:
    print(annual_report_df.head())
else:
    print("No annual reports available.")


# 📌 Plot Stock Price with Moving Averages
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], label="Close Price", color='blue', linewidth=1.5)
plt.plot(df.index, df['SMA_20'], label="SMA 20", color='orange', linestyle='dashed')
plt.plot(df.index, df['EMA_50'], label="EMA 50", color='red', linestyle='dotted')
plt.xlabel("Time")
plt.ylabel("Stock Price")
plt.title(f"{symbol} - Stock Price with Moving Averages")
plt.legend()
plt.grid()
plt.show()

# 📌 Plot RSI
plt.figure(figsize=(12, 4))
plt.plot(df.index, df['RSI_14'], label="RSI (14)", color='purple')
plt.axhline(70, linestyle='dashed', color='red', label="Overbought (70)")
plt.axhline(30, linestyle='dashed', color='green', label="Oversold (30)")
plt.xlabel("Time")
plt.ylabel("RSI")
plt.title(f"{symbol} - RSI Indicator")
plt.legend()
plt.grid()
plt.show()

# 📌 Plot VWAP
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], label="Close Price", color='blue')
plt.plot(df.index, df['VWAP'], label="VWAP", color='green', linestyle='dashed')
plt.xlabel("Time")
plt.ylabel("Price")
plt.title(f"{symbol} - VWAP vs Close Price")
plt.legend()
plt.grid()
plt.show()

# 📌 Market Movers Visualization
if len(market_movers) > 0:
    top_gainers = pd.DataFrame(market_movers).nlargest(10, 'close')
    top_losers = pd.DataFrame(market_movers).nsmallest(10, 'close')

    plt.figure(figsize=(12, 6))
    plt.bar(top_gainers['symbol'], top_gainers['close'], color='green', label="Top Gainers")
    plt.bar(top_losers['symbol'], top_losers['close'], color='red', label="Top Losers")
    plt.xlabel("Stock Symbols")
    plt.ylabel("Closing Price")
    plt.title("Top Gainers & Losers")
    plt.legend()
    plt.grid()
    plt.show()
