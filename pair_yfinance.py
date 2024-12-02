import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import coint
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

# Define the stock symbols
symbol_a = "GOOGL"  # Stock A (to be dynamically set)
symbol_b = "JPM"  # Stock B (to be dynamically set)

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



# Fetch the latest data again to ensure it's up-to-date
latest_data = yf.download([symbol_a, symbol_b], start=start_date, end=end_date)

# Access the latest data for MSFT and AAPL using multi-index format
latest_price_a = latest_data.iloc[-1][('Close', symbol_a)]
latest_price_b = latest_data.iloc[-1][('Close', symbol_b)]

print(f"Latest {symbol_a} price: {latest_price_a}")
print(f"Latest {symbol_b} price: {latest_price_b}")

# Calculate the latest spread
latest_spread = latest_price_a - beta * latest_price_b

# Calculate the rolling mean and standard deviation of the spread
window = 30  # Adjust the window size for rolling calculation
# spread_mean = prices['Spread'].rolling(window=window).mean().iloc[-1]
# spread_std = prices['Spread'].rolling(window=window).std().iloc[-1]
# Calculate the historic mean of the spread
# Calculate the historic mean of the spread
historic_mean_spread = prices["Spread"].mean()

# Calculate the present (latest) spread
latest_spread = latest_price_a - beta * latest_price_b

# Make sure the latest spread is a scalar value
latest_spread = float(latest_spread)

# Calculate the rolling mean and standard deviation of the spread
spread_mean = prices['Spread'].rolling(window=30).mean().iloc[-1]
spread_std = prices['Spread'].rolling(window=30).std().iloc[-1]

# Calculate the Z-score (spread - mean) / std
latest_z_score = (latest_spread - spread_mean) / spread_std

# Display historic and present mean spreads
print(f"Historic Mean of Spread: {historic_mean_spread:.2f}")
print(f"Present Mean (Latest Spread): {latest_spread:.2f}")

# Suggest a trade based on the Z-score
if latest_z_score > 1:
    position = f"Short {symbol_a}, Long {symbol_b}"  # Z-score above 1, symbol_a is overvalued, symbol_b is undervalued
    print(f"The Z-score is {latest_z_score:.2f}. Consider shorting {symbol_a} and going long on {symbol_b}.")
elif latest_z_score < -1:
    position = f"Long {symbol_a}, Short {symbol_b}"  # Z-score below -1, symbol_a is undervalued, symbol_b is overvalued
    print(f"The Z-score is {latest_z_score:.2f}. Consider long on {symbol_a} and shorting {symbol_b}.")
else:
    position = "No Position"  # Z-score between -1 and 1, suggests no action
    print(f"The Z-score is {latest_z_score:.2f}. No immediate action is suggested.")

plt.tight_layout()
plt.show()