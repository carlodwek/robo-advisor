# this is the "app/robo_advisor.py" file

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
        symbollist = []
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
            exit = False
            while True:
                try:
                    choice = float(input("What is your risk tolerance? [1-10, 10 being most risk tolerant] ") )
                    if choice > 0 and choice <= 10:
                        risk = 0.05 * float(choice)
                        break
                    else:
                         choice = input("Invalid risk tolerance. Would you like to try again? [y/n] ")
                         if choice.lower() != "y":
                             exit = True
                             break
                except:
                    choice = input("Invalid risk tolerance. Would you like to try again? [y/n] ")
                    if choice.lower() != "y":
                        exit = True
                        break
            if exit == True:
                break
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
                        if choice.lower() != "y":
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

                    df = Output(df, risk)

                    df = df.reset_index()
                    df["symbol"] = symbol
                    frames.append(df)
                    symbollist.append(symbol)
                    #DataVis(df) ##You can uncomment this if you want an individual chart for every stock

            print()
            choice = input("Would you like to plot all your stock prices on a chart? [y/n] ")
            if choice.lower() == "y":
                symbolstr = "-".join(symbollist)
                DataVis(frames, symbolstr)
            print()
            choice = input("Would you like to try again? [y/n] ")
            if choice.lower() != "y":
                break

def to_usd(my_price):
    return f"${my_price:,.2f}" #> $12,000.71

def Selection():
    symbols = []
    counter = 0
    while len(symbols)< 5:
        symbol = input("Please input a valid stock Symbol (input 'COMPLETE' when finished): ")
        symbol = symbol.upper()
        if symbol == "COMPLETE":
            break
        elif symbol in symbols:
            print("Symbol already selected.")
        elif len(symbol) < 10 and len(symbol) > 0: #international stock tickers are denoted by XXX.[Stock Exchange] (e.g. "IAG.LON") and therefore 5 should not be the max. In addition, they can be numeric (C6L.SGX)
            symbols.append(symbol)
        else:
            print("Invalid symbol. Please try again.")
    if len(symbols) == 5:
        print("Maximum symbols per request reached (5 requests/min API limit)")
    return symbols

def GetData(symbol, API_KEY):
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={API_KEY}"
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
            "close": float(daily_data["5. adjusted close"]),
            "volume": int(daily_data["6. volume"]),
        }
        records.append(record)
    return records, symbol

def Output(df, risk):
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
    closes = oneYdf["close"]
    high = max(closes)
    highstr = to_usd(high)
    low = min(closes)
    lowstr = to_usd(low)
    print("52W High/Low:", highstr+"/"+lowstr)

    ## Recommendation algorithm
    delta = high-low
    deltarisk = delta*risk
    #print(deltarisk)
    if close < (low+deltarisk):
        print("Recommendation: BUY")
        print("Reason: the latest price is", to_usd(deltarisk), "above the 52W low.")
    elif close > (high-deltarisk):
        print("Recommendation: SELL")
        print("Reason: the latest price is", to_usd(deltarisk), "below the 52W high.")
    else:
        print("Recommendation: HOLD")
        print("Reason: the latest price is neither", to_usd(deltarisk), "below the 52W high nor", to_usd(deltarisk), "above the 52W low.")

    return df

def DataVis(frames, symbolsstr):
    fulldf = pd.concat(frames)
    plt1 = sns.relplot(data=fulldf, x="timestamp", y="close", kind="line", hue="symbol").set(ylabel="Price", xlabel="Date")
    plt1.fig.subplots_adjust(top=.95)
    plt1.ax.set_title('Stock Prices Over Time')
    plt1._legend.set_title("Symbol")
    path = "./charts"
    filename = f"{symbolsstr}.png"
    plt.savefig(os.path.join(path, filename))
    print("Chart saved successfully. Close chart window to continue.")
    plt.show()

main()
