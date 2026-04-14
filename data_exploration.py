import requests
import pandas as pd
import time
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("ALPHAVANTAGE_API_KEY")

tickers = ["AMZN", "MSFT", "AAPL", "NVDA", "TSLA"]

def clean_data():
    rows = []
    for ticker in tickers:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}"
        r = requests.get(url)
        data = r.json()

        # print(data)

        time_series = data["Time Series (Daily)"]

        for date, values in time_series.items():
            row = {
                "ticker": ticker,
                "date": date,
                "open": values["1. open"],
                "close": values["4. close"],
                "high": values["2. high"],
                "low": values["3. low"],
                "volume": values["5. volume"]
            }
            rows.append(row)
        time.sleep(5)

    df = pd.DataFrame(rows)

    df["date"] = pd.to_datetime(df["date"])
    df[["open", "close", "high", "low", "volume"]] = df[["open", "close", "high", "low", "volume"]].apply(pd.to_numeric)

    return df

# print(df.head())

    

