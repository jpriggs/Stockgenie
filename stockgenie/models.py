import json
import requests
from datetime import datetime
import numpy as np
from sklearn import linear_model

class ApiStockData():

    def __init__(self, timeStamp, price, function):

        # Formats the datetime value to match either an intraday or daily stock value
        if function == 'TIME_SERIES_INTRADAY':
            self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
        else:
            self.timeStampValue = datetime.strptime(timeStamp, '%Y-%m-%d')
        self.priceValue = float(price)

class Regression():

    def __init__(self, dataset, interval, function):
        self.timeStampList = dataset.index
        self.priceList = [price for price in dataset.Price]
        self.timeDeltaList = [index for index, timeStamp in enumerate(self.timeStampList)]
        self.timeInterval = interval
        self.apiLookupFunction = function

        self.linearModel = linear_model.LinearRegression()
        self.times = np.reshape(self.timeDeltaList, (len(self.timeDeltaList), 1))
        self.prices = np.reshape(self.priceList, (len(self.priceList), 1))
        self.linearModel.fit(self.times, self.prices)

    def calculateRegressionLine(self):

        # Create linear model data
        linearFitPricesMatrix = self.linearModel.predict(self.times)
        regressionLineData = [column for row in linearFitPricesMatrix for column in row]

        return regressionLineData

    def calculatePricePrediction(self):

        predictTimeStamp = 0
        predictTimeMultiplier = 0

        if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
            predictTimeMultiplier = 1.1 # Predicts 10 minutes ahead
            predictTimeStamp = (((self.timeInterval * predictTimeMultiplier) * len(self.timeStampList)) - 1)
        else:
            predictTimeMultiplier = 2 # Predicts 200 days ahead
            predictTimeStamp = (((self.timeInterval * predictTimeMultiplier) * len(self.timeStampList)) - 1)

        pricePredictionMatrix = self.linearModel.predict(predictTimeStamp)
        pricePrediction = [column for row in pricePredictionMatrix for column in row]

        return pricePrediction

class UserSearchData():

    def __init__(self, text, interval, function):
        self.sanitizedSearchString = text.lower()
        self.sanitizedSearchString = ''.join(character for character in self.sanitizedSearchString if character.isalnum())
        self.apiLookupFunction = function

        # Formats the interval query used in the API url based hitting the intraday or daily API
        if function == 'TIME_SERIES_INTRADAY':
            self.timeInterval = interval
        else:
            self.timeInterval = 1

    def switchLookupFunction(self):

        if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
            self.apiLookupFunction = 'TIME_SERIES_DAILY'
        else:
            self.apiLookupFunction = 'TIME_SERIES_INTRADAY'
            self.timeInterval = 1

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
