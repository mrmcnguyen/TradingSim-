import requests
import json

def search_stocks(search_term): # Returns a list of stocks associated with search term
    stocks = []
    #url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={search_term}&apikey=demo'
    url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tesco&apikey=demo'
    r = requests.get(url)
    data = r.json()
    # Extract "symbol" and "symbol name" pairs
    symbol_name_pairs = [(match.get("1. symbol"), match.get("2. name")) for match in data.get("bestMatches", [])]
    
    # Create strings for each pair and add to the stocks list
    stocks = [f"{symbol} - {name}" for symbol, name in symbol_name_pairs]

    return stocks

def get_info(ticker):
    
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo'
    r = requests.get(url)
    data = r.json()

    return data
