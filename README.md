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

You will need an API Key to run the program. Go to [AlphaVantage API](https://www.alphavantage.co) and sign up for an API key. You should then set an environment variable called `ALPHAVANTAGE_API_KEY` in your local repo in a ".env" file.

```
ALPHAVANTAGE_API_KEY="<Your API Key>"
```

## Instructions

Run the program from the command-line:

```sh
python app/robo_advisor.py
```
