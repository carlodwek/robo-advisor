# this is the "app/robo_advisor.py" file

# print("-------------------------")
# print("SELECTED SYMBOL: XYZ")
# print("-------------------------")
# print("REQUESTING STOCK MARKET DATA...")
# print("REQUEST AT: 2018-02-20 02:00pm")
# print("-------------------------")
# print("LATEST DAY: 2018-02-20")
# print("LATEST CLOSE: $100,000.00")
# print("RECENT HIGH: $101,000.00")
# print("RECENT LOW: $99,000.00")
# print("-------------------------")
# print("RECOMMENDATION: BUY!")
# print("RECOMMENDATION REASON: TODO")
# print("-------------------------")
# print("HAPPY INVESTING!")
# print("-------------------------")
print("Robo Advisor Initializing...")

import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from datetime import date
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt

load_dotenv()

def main():

    sns.set_theme()
    while True:
        frames = []
        print("----------------------------")
        print("Symbol Selection")
        symbols = Selection()
        API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", default="Err")
        amt = len(symbols)
        if amt == 0:
            choice = input("No symbols inputed. Try again? [y/n] ")
            if choice.lower() != "y":
                break
        elif API_KEY == "Err":
            print("No API Key setup. Please set up and try again.")
            break
        else:
            risk = 0.05 * int(input("What is your risk tolerance? [1-10, 10 being most risk tolerant] "))
            counter = 0
            for i in symbols:
                print()
                counter += 1
                data = GetData(i, API_KEY)
                if data == "Err":
                    if counter == amt:
                        break
                    else:
                        choice = input("Would you like to continue? [y/n] ")
                        if choice != "y":
                            break
                else:

                    records, symbol = ArrangeData(data)

                    df = pd.DataFrame(records)
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d")
                    #print(df)

                    path = "./data"
                    filename = "prices_"+symbol.lower()+".csv"
                    df.to_csv(os.path.join(path, filename), index=False)
                    print(symbol, "downloaded successfully.")

                    now = datetime.now()
                    nowdate = now.strftime('%d %B %Y')
                    nowtime = now.strftime('%X')
                    print("Run at:", nowtime, "on", nowdate)

                    timestamps = df["timestamp"]
                    lastr = timestamps[0]
                    #lastrdt = datetime.strptime(lastr, '%Y-%m-%d %H:%M:%S')
                    rdate = lastr.strftime('%d %B %Y')
                    print("Latest data from:", rdate)

                    closes = df["close"]
                    close = closes[0]
                    closestr = to_usd(close)
                    print("Last closing price:", closestr)

                    # highs = df["high"]
                    # highs = highs[:100]
                    # high = to_usd(max(highs))
                    # print("Recent high:", high)
                    #
                    # lows = df["low"]
                    # lows = lows[:100]
                    # low = to_usd(min(lows))
                    # print("Recent low:", low)

                    oneY = lastr-timedelta(days=365)
                    #oneY = oneYdt.strftime('%Y-%m-%d')
                    df.set_index("timestamp", inplace=True)
                    oneYdf = df.loc[:oneY]
                    highlow = oneYdf[["high","low"]]
                    highs = highlow["high"]
                    high = max(highs)
                    highstr = to_usd(high)
                    lows = highlow["low"]
                    low = min(lows)
                    lowstr = to_usd(low)
                    print("52W High/Low:", highstr+"/"+lowstr)

                    ## Recommendation algorithm
                    delta = high-low
                    deltarisk = delta*risk
                    #print(deltarisk)
                    if close < (low+deltarisk):
                        print("Recommendation: BUY")
                    elif close > (high-deltarisk):
                        print("Recommendation: SELL")
                    else:
                        print("Recommendation: HOLD")
                    ##Plotting

                    df = df.reset_index()
                    #df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d")
                    df["symbol"] = symbol
                    frames.append(df)

                    # sns.relplot(
                    #     data=df,
                    #     x="timestamp", y="close", kind="line"
                    # )
                    # plt.show()
            fulldf = pd.concat(frames)
            sns.relplot(data=fulldf, x="timestamp", y="close", kind="line", hue="symbol")
            plt.show()
            print()
            choice = input("Would you like to try again? [y/n] ")
            if choice.lower() != "y":
                break

def to_usd(my_price):
    return f"${my_price:,.2f}" #> $12,000.71

def Selection():
    symbols = []
    counter = 0
    while counter < 5:
        symbol = input("Please input a valid stock Symbol (input 'COMPLETE' when finished): ")
        counter += 1
        symbol = symbol.upper()
        if symbol == "COMPLETE":
            break
        elif len(symbol) < 10 and len(symbol) > 0: #international stock tickers are denoted by XXX.[Stock Exchange] (e.g. "IAG.LON") and therefore 5 should not be the max. In addition, they can be numeric (C6L.SGX)
            symbols.append(symbol)
        else:
            print("Invalid symbol. Please try again.")
    if counter == 5:
        print("Maximum symbols per request reached (5 requests/min API limit)")
    return symbols

def GetData(symbol, API_KEY):
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"
    response = requests.get(request_url)
    #print(type(response))
    #print(response.status_code)
    data = json.loads(response.text)
    #print(type(data))
    if 'Error Message' in data:
        print(symbol, "symbol not found.")
        return "Err"
    else:
        return data

def ArrangeData(data):
    mdata = data["Meta Data"]
    symbol = mdata["2. Symbol"]
    #lastr = mdata["3. Last Refreshed"]
    prices = data["Time Series (Daily)"]
    records = []
    for date, daily_data in prices.items():
        record = {
            "timestamp": date,
            "open": float(daily_data["1. open"]),
            "high": float(daily_data["2. high"]),
            "low": float(daily_data["3. low"]),
            "close": float(daily_data["4. close"]),
            "volume": int(daily_data["5. volume"]),
        }
        records.append(record)
    return records, symbol

main()
