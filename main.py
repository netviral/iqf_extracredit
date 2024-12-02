# import requests
# import pandas as pd
# from statsmodels.tsa.stattools import coint
# import matplotlib.pyplot as plt

# # Alpha Vantage API Key
# API_KEY = "X7VEW6A6AOJ76JQR"
# symbol_a = "XOM"  # Stock A
# symbol_b = "CVX"  # Stock B

# # Fetch daily historical price data
# def fetch_data(symbol, start_date, end_date):
#     url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full"
#     response = requests.get(url)
#     data = response.json()
#     print(f"API response for {symbol}: {data}")  # Debugging: Print full response
    
#     if "Time Series (Daily)" in data:
#         df = pd.DataFrame(data["Time Series (Daily)"]).T.astype(float)
#         df.index = pd.to_datetime(df.index)
#         df.sort_index(inplace=True)
#         df = df.rename(columns={"4. close": f"{symbol}_close"})
#         return df[[f"{symbol}_close"]]
#     else:
#         raise ValueError(f"Error fetching data for {symbol}: {data.get('Note', 'No data returned')}")
    
# # Define the date range
# start_date = "2004-01-01"
# end_date = "2023-12-31"

# # Fetch historical price data
# df_a = fetch_data(symbol_a, start_date, end_date)
# df_b = fetch_data(symbol_b, start_date, end_date)

# # Merge datasets on timestamp
# prices = pd.merge(df_a, df_b, left_index=True, right_index=True)

# # Perform Cointegration Test
# score, p_value, _ = coint(prices[f"{symbol_a}_close"], prices[f"{symbol_b}_close"])
# print(f"Cointegration Test p-value: {p_value}")

# # If p-value < 0.05, the series are cointegrated (stationary spread)
# if p_value < 0.05:
#     print(f"The pair {symbol_a} and {symbol_b} are cointegrated. Suitable for mean-reversion strategy.")
# else:
#     print(f"The pair {symbol_a} and {symbol_b} are not cointegrated. Consider using another pair.")

# # Plot the price data if cointegrated
# plt.figure(figsize=(14, 7))
# plt.plot(prices.index, prices[f"{symbol_a}_close"], label=f"{symbol_a} Price", color="blue")
# plt.plot(prices.index, prices[f"{symbol_b}_close"], label=f"{symbol_b} Price", color="red")
# plt.title(f"Price Data for {symbol_a} and {symbol_b} (2004-2023)")
# plt.xlabel("Date")
# plt.ylabel("Price")
# plt.legend()
# plt.show()
