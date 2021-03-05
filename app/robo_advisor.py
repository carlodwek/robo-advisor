# this is the "app/robo_advisor.py" file

print("-------------------------")
print("SELECTED SYMBOL: XYZ")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print("REQUEST AT: 2018-02-20 02:00pm")
print("-------------------------")
print("LATEST DAY: 2018-02-20")
print("LATEST CLOSE: $100,000.00")
print("RECENT HIGH: $101,000.00")
print("RECENT LOW: $99,000.00")
print("-------------------------")
print("RECOMMENDATION: BUY!")
print("RECOMMENDATION REASON: TODO")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")

import requests
import json
import pandas
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("Robo Advisor Initializing")
    print("-------------------------")
    while True:


        print("Symbol Selection")
        symbols = Selection()
        if len(symbols) == 0:
            print("No symbols inputed.")
        else:
            data = GetData(symbols)
            #print(data)
            arrangeddata = ArrangeData(data)
            for i in arrangeddata:
                print(i.keys())
        break
def Selection():
    symbols = []
    while True:
        symbol = input("Please input a valid stock Symbol (input 'COMPLETE' when finished): ")
        symbol = symbol.upper()
        if symbol == "COMPLETE":
            break
        elif len(symbol) < 5:
            symbols.append(symbol)
        else:
            print("Invalid symbol. Please try again.")
    return symbols

def GetData(symbols):
    data = []
    API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", default="Err")
    if API_KEY == "Err":
        print("No API Key setup")
    else:
        for symbol in symbols:
            request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&interval=5min&apikey={API_KEY}"
            response = requests.get(request_url)
            print(type(response))
            print(response.status_code)
            parsed = json.loads(response.text)
            print(type(parsed))
            if 'Error Message' in parsed:
                print(symbol, "symbol not found.")
            else:
                data.append(parsed)
    return data

def ArrangeData(data):
    arrangeddata = []
    for i in data:
        mdata = i["Meta Data"]
        symbol = mdata["2. Symbol"]
        prices = i["Time Series (Daily)"]
        records = []
        for date, daily_data in prices.items():
            record = {
                "date": date,
                "open": float(daily_data["1. open"]),
                "high": float(daily_data["2. high"]),
                "low": float(daily_data["3. low"]),
                "close": float(daily_data["4. close"]),
                "volume": int(daily_data["5. volume"]),
            }
            records.append(record)
        symbolrecords = {symbol: records}
        print(symbolrecords)
        arrangeddata.append(symbolrecords)
    return arrangeddata

main()
