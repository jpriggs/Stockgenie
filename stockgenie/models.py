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

        self.stockSymbol = symbol
        self.companyName = name
        self.stockExchange = exchange

        self.sanitizedStockSymbol = self.sanitizeValue(symbol)
        self.sanitizedCompanyName = self.sanitizeValue(name)
        self.sanitizedStockExchange = self.sanitizeValue(exchange)

    def sanitizeValue(self, valToSanitize):
        valToSanitize = valToSanitize.lower()
        return ''.join(character for character in valToSanitize if character.isalnum())

    def replaceCaretSymbol(self, valToReplace):
        return valToReplace.replace('^','-')

    def matchesNameOrSymbol(self, searchValue):
        return self.sanitizedStockSymbol == searchValue or self.sanitizedCompanyName == searchValue

