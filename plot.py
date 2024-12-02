import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Define stock symbols
symbol_a = "MSFT"  # Stock A
symbol_b = "AAPL"  # Stock B

# Function to fetch data from Yahoo Finance
def fetch_data(symbol):
    data = yf.download(symbol, start="2004-01-01", end="2023-12-31")
    df = data[['Close']]  # Only use 'Close' price
    df = df.rename(columns={"Close": f"{symbol}_close"})
    return df

# Fetch historical price data
df_a = fetch_data(symbol_a)
df_b = fetch_data(symbol_b)

# Merge datasets on timestamp
prices = pd.merge(df_a, df_b, left_index=True, right_index=True)

# Debugging: check the shapes of the price data
print(f"Shape of {symbol_a} price data: {df_a.shape}")
print(f"Shape of {symbol_b} price data: {df_b.shape}")
print(f"Shape of merged price data: {prices.shape}")

# Regression to find hedge ratio
X = prices[f"{symbol_b}_close"].values.reshape(-1, 1)
y = prices[f"{symbol_a}_close"].values
model = LinearRegression().fit(X, y)
beta = model.coef_[0]

# Debugging: check the beta value
print(f"Hedge ratio (beta): {beta}")

# Calculate the spread (ensure it's a single column)
prices["Spread"] = prices[f"{symbol_a}_close"].values - (beta * prices[f"{symbol_b}_close"].values)

# Check if 'Spread' was calculated correctly
print(f"First few rows of spread:\n{prices['Spread'].head()}")

# Plot the prices and spread
plt.figure(figsize=(14, 7))

# Plot stock prices
plt.subplot(2, 1, 1)
plt.plot(prices.index, prices[f"{symbol_a}_close"], label=symbol_a, color="blue")
plt.plot(prices.index, prices[f"{symbol_b}_close"], label=symbol_b, color="red")
plt.title(f"Stock Prices: {symbol_a} vs {symbol_b}")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()

# Plot spread
plt.subplot(2, 1, 2)
plt.plot(prices.index, prices["Spread"], color="orange", label="Spread")
plt.axhline(prices["Spread"].mean(), color="red", linestyle="--", label="Mean Spread")
plt.axhline(prices["Spread"].mean() + prices["Spread"].std(), color="green", linestyle="--", label="Mean + 1 Std")
plt.axhline(prices["Spread"].mean() - prices["Spread"].std(), color="green", linestyle="--", label="Mean - 1 Std")
plt.title("Spread Between Stocks")
plt.xlabel("Date")
plt.ylabel("Spread")
plt.legend()

plt.tight_layout()
plt.show()
