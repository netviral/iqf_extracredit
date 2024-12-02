# THIS FILE FINDS COINTEGRATED PAIRS
import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import coint
import itertools

# Define a list of stock symbols (e.g., S&P 500, or any sector of your choice)
symbols = ["XOM", "CVX", "GOOGL", "MSFT", "AAPL", "AMZN", "JPM", "BAC"]

# Define the date range
start_date = "2020-01-01"
end_date = "2024-12-31"

# Fetch historical price data using Yahoo Finance
def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data = data[['Close']]  # Get only the 'Close' prices
    data = data.rename(columns={"Close": f"{symbol}_close"})
    return data

# Fetch data for all symbols
prices = {}
for symbol in symbols:
    prices[symbol] = fetch_data(symbol, start_date, end_date)

# Merge datasets on timestamp
merged_prices = pd.concat(prices.values(), axis=1, join='inner')

# Function to perform cointegration test on a pair of stocks
def test_cointegration(pair, data):
    stock_a, stock_b = pair
    score, p_value, _ = coint(data[f"{stock_a}_close"], data[f"{stock_b}_close"])
    return p_value

# Check all pairs of stocks for cointegration
cointegrated_pairs = []
for pair in itertools.combinations(symbols, 2):
    p_value = test_cointegration(pair, merged_prices)
    if p_value < 0.05:  # If p-value < 0.05, the pair is cointegrated
        cointegrated_pairs.append((pair, p_value))

# Print the cointegrated pairs
for pair, p_value in cointegrated_pairs:
    print(f"Pair: {pair}, p-value: {p_value}")

