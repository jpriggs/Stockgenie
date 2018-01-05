import json
import requests
from datetime import datetime

class ApiStockData():

    def __init__(self, timeStamp, price):
        self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        self.priceValue = float(price)

class UserSearchData():

    def __init__(self, text):
        self.searchData = text.lower()
        self.searchData = ''.join(x for x in self.searchData if x.isalnum())

class StockListData():

    def __init__(self, symbol, name, exchange):

        self.stockSymbol = symbol.lower()
        self.stockSymbol = ''.join(x for x in self.stockSymbol if x.isalnum())
        self.companyName = name.lower()
        self.companyName = ''.join(x for x in self.companyName if x.isalnum())
        self.stockExchange = exchange.lower()
        self.stockExchange = ''.join(x for x in self.stockExchange if x.isalnum())
