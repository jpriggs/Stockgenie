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
        self.searchData = ''.join(char for char in self.searchData if char.isalnum())

class StockListData():

    def __init__(self, symbol, name, exchange):

        self.stockSymbol = symbol.lower()
        self.stockSymbol = ''.join(char for char in self.stockSymbol if char.isalnum())
        self.companyName = name.lower()
        self.companyName = ''.join(char for char in self.companyName if char.isalnum())
        self.stockExchange = exchange.lower()
        self.stockExchange = ''.join(char for char in self.stockExchange if char.isalnum())
