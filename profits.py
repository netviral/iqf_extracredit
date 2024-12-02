import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import coint
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

# Define the stock symbols
symbol_a = "GOOGL"  # Stock A
symbol_b = "JPM"    # Stock B

# Define the date range
start_date = "2020-01-01"
end_date = "2024-12-31"

# Fetch historical price data using Yahoo Finance
def fetch_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data = data[['Close']]  # Get only the 'Close' prices
    data = data.rename(columns={"Close": f"{symbol}_close"})
    return data

# Fetch historical price data for both stocks
df_a = fetch_data(symbol_a, start_date, end_date)
df_b = fetch_data(symbol_b, start_date, end_date)

# Merge datasets on timestamp
prices = pd.merge(df_a, df_b, left_index=True, right_index=True)

# Perform Cointegration Test
score, p_value, _ = coint(prices[f"{symbol_a}_close"], prices[f"{symbol_b}_close"])
print(f"Cointegration Test p-value: {p_value}")

# If p-value < 0.05, the series are cointegrated (stationary spread)
if p_value < 0.05:
    print(f"The pair {symbol_a} and {symbol_b} are cointegrated. Suitable for mean-reversion strategy.")
else:
    print(f"The pair {symbol_a} and {symbol_b} are not cointegrated. Consider using another pair.")

# Perform Linear Regression to calculate the hedge ratio (beta)
X = prices[f"{symbol_b}_close"].values.reshape(-1, 1)
y = prices[f"{symbol_a}_close"].values
model = LinearRegression().fit(X, y)
beta = model.coef_[0]

# Calculate the spread using element-wise operations (ensuring the correct shapes)
spread = (prices[f"{symbol_a}_close"].values - beta * prices[f"{symbol_b}_close"].values).flatten()

# Now, assign the spread as a pandas Series
prices["Spread"] = pd.Series(spread, index=prices.index)

# Calculate the Z-score of the spread
mean_spread = prices["Spread"].mean()
std_spread = prices["Spread"].std()
prices["Z-score"] = (prices["Spread"] - mean_spread) / std_spread

# Plot the price data and Z-score
plt.figure(figsize=(14, 7))

# Plot stock prices
plt.subplot(2, 1, 1)
plt.plot(prices.index, prices[f"{symbol_a}_close"], label=f"{symbol_a} Price", color="blue")
plt.plot(prices.index, prices[f"{symbol_b}_close"], label=f"{symbol_b} Price", color="red")
plt.title(f"Price Data for {symbol_a} and {symbol_b} (2004-2023)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()

# Plot Z-score
plt.subplot(2, 1, 2)
plt.plot(prices.index, prices["Z-score"], color="green", label="Z-score of Spread")
plt.axhline(0, color="black", linestyle="--", label="Mean (0 Z-score)")
plt.title(f"Z-score of Spread between {symbol_a} and {symbol_b}")
plt.xlabel("Date")
plt.ylabel("Z-score")
plt.legend()

plt.tight_layout()
# plt.show()

# Fetch the latest data again to ensure it's up-to-date
latest_data = yf.download([symbol_a, symbol_b], start=start_date, end=end_date)

# Print the multi-index column names to inspect
print(latest_data.columns)

# Access the latest data for GOOGL and JPM using multi-index format
latest_price_a = latest_data.iloc[-1][('Close', symbol_a)]
latest_price_b = latest_data.iloc[-1][('Close', symbol_b)]

print(f"Latest {symbol_a} price: {latest_price_a}")
print(f"Latest {symbol_b} price: {latest_price_b}")

# Calculate the latest spread
latest_spread = latest_price_a - beta * latest_price_b

# Calculate the rolling mean and standard deviation of the spread
window = 30  # Adjust the window size for rolling calculation
spread_mean = prices['Spread'].rolling(window=window).mean().iloc[-1]
spread_std = prices['Spread'].rolling(window=window).std().iloc[-1]

# Calculate the Z-score (spread - mean) / std
latest_z_score = (latest_spread - spread_mean) / spread_std
latest_z_score=latest_z_score[0]
# Print the Z-score
print(f"The Z-score is {latest_z_score:.2f}.")

# Define the trade size (number of shares)
trade_size = 20  # You can adjust this depending on how much capital you want to allocate

# Entry points for the trade (when spread deviates significantly from mean)
entry_spread = prices["Spread"].iloc[-1]  # Latest spread
entry_z_score = prices["Z-score"].iloc[-1]  # Latest Z-score

# Exit points when the spread reverts to the historical mean
exit_spread = prices["Spread"].mean()  # Historic mean of the spread

# Initialize trade counters and profit tracking
long_positions = 0
short_positions = 0
total_profit = 0
long_trade_details = []
short_trade_details = []

# Get the latest prices for GOOGL and JPM
latest_price_googl = latest_data.iloc[-1][('Close', symbol_a)]
latest_price_jpm = latest_data.iloc[-1][('Close', symbol_b)]

# Entry prices for GOOGL and JPM based on Z-score signal
if entry_z_score < -1:  # Suggest long on GOOGL and short on JPM
    entry_price_googl = latest_price_googl
    entry_price_jpm = latest_price_jpm
    exit_price_googl = entry_price_googl + (exit_spread - entry_spread)  # Expected price after mean reversion
    exit_price_jpm = entry_price_jpm - (exit_spread - entry_spread)  # Expected price after mean reversion

    # Calculate profit for GOOGL (long) and JPM (short)
    profit_googl = (exit_price_googl - entry_price_googl) * trade_size
    profit_jpm = (entry_price_jpm - exit_price_jpm) * trade_size

    # Total profit from this trade
    total_profit = profit_googl + profit_jpm

    # Track trade details
    long_positions += 1
    short_positions += 1
    long_trade_details.append({
        "Entry Price": entry_price_googl,
        "Exit Price": exit_price_googl,
        "Profit": profit_googl
    })
    short_trade_details.append({
        "Entry Price": entry_price_jpm,
        "Exit Price": exit_price_jpm,
        "Profit": profit_jpm
    })

    print(f"Profit from GOOGL (long): {profit_googl:.2f}")
    print(f"Profit from JPM (short): {profit_jpm:.2f}")
    print(f"Total Profit from the pair trade: {total_profit:.2f}")
else:
    print("No significant deviation in spread, no trade made.")

# Show the details of the trades
print("\n--- Long Positions ---")
for trade in long_trade_details:
    print(f"Entry Price: {trade['Entry Price']:.2f}, Exit Price: {trade['Exit Price']:.2f}, Profit: {trade['Profit']:.2f}")

print("\n--- Short Positions ---")
for trade in short_trade_details:
    print(f"Entry Price: {trade['Entry Price']:.2f}, Exit Price: {trade['Exit Price']:.2f}, Profit: {trade['Profit']:.2f}")

