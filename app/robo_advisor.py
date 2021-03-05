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

import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from datetime import date
from datetime import timedelta

load_dotenv()

def main():
    print("Robo Advisor Initializing")

    while True:
        print("-------------------------")
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
            counter = 0
            for i in symbols:
                print()
                counter += 1
                data = GetData(i, API_KEY)
                #print(data)
                if data == "Err":
                    if counter == amt:
                        break
                    else:
                        choice = input("Would you like to continue? [y/n] ")
                        if choice != "y":
                            break
                else:

                    records, symbol, lastr = ArrangeData(data)

                    df = pd.DataFrame(records)
                    #print(df)

                    path = "./data"
                    filename = "prices_"+symbol.lower()+".csv"
                    df.to_csv(os.path.join(path, filename), index=False)
                    print(symbol, "downloaded successfully.")

                    now = datetime.now()
                    nowdate = now.strftime('%d %B %Y')
                    nowtime = now.strftime('%X')
                    print("Run at:", nowtime, "on", nowdate)

                    lastrdt = datetime.strptime(lastr, '%Y-%m-%d')
                    rdate = lastrdt.strftime('%d %B %Y')
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

                    oneYdt = lastrdt-timedelta(days=365)
                    oneY = oneYdt.strftime('%Y-%m-%d')
                    highlow = df[["timestamp","high","low"]]
                    highlow.set_index("timestamp", inplace=True)
                    highlow = highlow.loc[:oneY]
                    highs = highlow["high"]
                    high = max(highs)
                    highstr = to_usd(high)
                    lows = highlow["low"]
                    low = min(lows)
                    lowstr = to_usd(low)
                    print("52W High/Low:", highstr+"/"+lowstr)

                    ## Recommendation algorithm
                    delta = high-low
                    risk = 0.2
                    deltarisk = delta*risk
                    #print(deltarisk)
                    if close < (low+deltarisk):
                        print("Recommendation: BUY")
                    elif close > (high-deltarisk):
                        print("Recommendation: SELL")
                    else:
                        print("Recommendation: HOLD")
                    ##Plotting
                    

            print()
            choice = input("Would you like to try again? [y/n] ")
            if choice.lower() != "y":
                break

def to_usd(my_price):
    return f"${my_price:,.2f}" #> $12,000.71

def Selection():
    symbols = []
    while True:
        symbol = input("Please input a valid stock Symbol (input 'COMPLETE' when finished): ")
        symbol = symbol.upper()
        if symbol == "COMPLETE":
            break
        elif len(symbol) < 10 and len(symbol) > 0: #international stock tickers are denoted by XXX.[Stock Exchange] (e.g. "IAG.LON") and therefore 5 should not be the max. In addition, they can be numeric (C6L.SGX)
            symbols.append(symbol)
        else:
            print("Invalid symbol. Please try again.")
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
    lastr = mdata["3. Last Refreshed"]
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
    return records, symbol, lastr

main()
