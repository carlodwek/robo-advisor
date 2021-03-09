# Robo-Advisor Project

## Summary

This is a Python application that provides clients with automatic stock trading recommendations.

## Setup

### Repo Setup

Clone this repo to your computer.

After cloning the repo, navigate there from the command-line:

```sh
cd ~/[File Location]/robo-advisor
```

### Environment Setup

Create and activate a new project-specific Anaconda virtual environment:

```sh
conda create -n stocks-env python=3.8 # (first time only)
conda activate stocks-env
```

Download the required packages (first time only):

```sh
pip install -r requirements.txt
```

### Enviroment Variable - API Key

You will need an API Key to run the program. Go to [AlphaVantage API](https://www.alphavantage.co) and sign up for an API key. You should then set an environment variable called `ALPHAVANTAGE_API_KEY` in your local repo in a file named ".env".

```
ALPHAVANTAGE_API_KEY="<Your API Key>"
```

## Instructions

Run the program from the command-line:

```sh
python app/robo_advisor.py
```

Input up to 5 different symbols. Input "COMPLETE" when finished (not case-sensitive).

Input a risk tolerance between 1 and 10 (10 being most risk tolerant).
The program will then download and save the stock price data in a csv file in the data folder.

It will also output various key facts and a robo recommendation. This recommendation is based on your risk tolerance and is calculating by taking the difference between the 52W High and Low and multiplying it by (%5 x your risk tolerance). If the current price is below the high by at most this amount, it will recommend a sell. If it is at most above the low by this amount, it will recommend a buy. Else, it will recommend a hold.

Input whether or not you want to plot the prices on a chart. If you choose this option it will show the chart in a window as well as saving it in the charts folder as a png.

Enjoy the advisor!
