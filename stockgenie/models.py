import json
import requests
from datetime import datetime

class ApiStockData():

    def __init__(self, timeStamp, price):
        self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        self.priceValue = float(price)

class UserSearchData():

    def __init__(self, text):
        self.sanitizedSearchString = text.lower()
        self.sanitizedSearchString = ''.join(character for character in self.sanitizedSearchString if character.isalnum())

class StockListData():

    def __init__(self, symbol, name, exchange):

        self.stockSymbol = symbol.lower()
        self.stockSymbol = ''.join(character for character in self.stockSymbol if character.isalnum())
        self.companyName = name.lower()
        self.companyName = ''.join(character for character in self.companyName if character.isalnum())
        self.stockExchange = exchange.lower()
        self.stockExchange = ''.join(character for character in self.stockExchange if character.isalnum())
