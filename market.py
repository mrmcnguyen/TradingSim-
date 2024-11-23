import requests
import json


def search_stocks(search_term): # Returns a list of stocks associated with search term
    stocks = []
    #url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={search_term}&apikey=DKNFKQ8CGWZMRZSO'
    url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo'
    r = requests.get(url)
    data = r.json()
    # Extract "symbol" and "symbol name" pairs
    symbol_name_pairs = [(match.get("1. symbol"), match.get("2. name")) for match in data.get("bestMatches", [])]
   
    # Create strings for each pair and add to the stocks list
    stocks = [f"{symbol} - {name}" for symbol, name in symbol_name_pairs]

    return stocks

def get_info(ticker):
   
    #url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey=DKNFKQ8CGWZMRZSO'
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo'
    r = requests.get(url)
    data = r.json()

    return data

def get_ticker_price(ticker):
    ticker_price = float(get_info(ticker)['Global Quote']['05. price'])
    return ticker_price

def calculate_price(ticker, quantity, order_type):
    ticker_price = float(get_info(ticker)['Global Quote']['05. price'])
    return ticker_price * quantity

def get_top_movers():
    movers = []
    #url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=DKNFKQ8CGWZMRZSO'
    url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=demo'
    r = requests.get(url)
    data = r.json()


    top_gainers = data['top_gainers'][:3]
    top_losers = data['top_losers'][:3]


    for i in top_gainers:
        movers.append(i)


    for i in top_losers:
        movers.append(i)


    return movers



