import json
import requests
from datetime import datetime

class ApiStockData():

    def __init__(self, timeStamp, price, function):

        # Formats the datetime value to match either an intraday or daily stock value
        if function == 'TIME_SERIES_INTRADAY':
            self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        else:
            self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d')
        self.priceValue = float(price)

class UserSearchData():

    def __init__(self, text, interval, function):
        self.sanitizedSearchString = text.lower()
        self.sanitizedSearchString = ''.join(character for character in self.sanitizedSearchString if character.isalnum())
        self.apiLookupFunction = function

        # Formats the interval query used in the API url based hitting the intraday or daily API 
        if function == 'TIME_SERIES_INTRADAY':
            self.timeInterval = str(interval) + 'min'
        else:
            self.timeInterval = "''"

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

    def getApiSafeSymbol(self, valToReplace):
        return valToReplace.replace('^','-')

    def getChartSafeTitleLength(self, valToSanitize):
        baseTitleLength = 32
        for character in valToSanitize[baseTitleLength:]:
            if valToSanitize[baseTitleLength - 1:baseTitleLength] is not ' ':
                baseTitleLength += 1
            else:
                baseTitleLength -= 1
            break
        return valToSanitize[:baseTitleLength]

    def matchesNameOrSymbol(self, searchValue):
        return self.sanitizedStockSymbol == searchValue or self.sanitizedCompanyName == searchValue
