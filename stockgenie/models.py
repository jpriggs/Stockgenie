import json
import requests
from datetime import datetime, time, timedelta
import numpy as np
from sklearn import linear_model
from pandas.tseries.offsets import CustomBusinessHour, CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

class ApiStockData():

    def __init__(self, timeStamp, price, function):

        # Formats the datetime value to match either an intraday or daily stock value
        dtFormat = '%Y-%m-%d'
        if function == 'TIME_SERIES_INTRADAY':
            dtFormat = '%Y-%m-%d %H:%M:%S'
        self.timeStampValue = datetime.strptime(timeStamp, dtFormat)
        self.priceValue = float(price)

class Regression():

    def __init__(self, dataset, interval, function):
        self.timeStampList = dataset.index
        self.timeStampValue = range(0, len(self.timeStampList))
        self.timeInterval = interval
        self.apiLookupFunction = function

        self.times = np.reshape(self.timeStampValue, (len(self.timeStampValue), 1))
        self.prices = np.reshape(dataset.Price, (len(dataset.Price), 1))

        self.linearModel = linear_model.LinearRegression()
        self.linearModel.fit(self.times, self.prices)

    def calculateRegressionLine(self):
        # Create linear model data
        linearFitPricesMatrix = self.linearModel.predict(self.times)
        regressionLineData = [column for row in linearFitPricesMatrix for column in row]
        return regressionLineData

    def calculatePricePrediction(self):
        # Market opens at 9:30, closes at 16:00
        # Closed on weekends and national holidays
        # Code has to calculate and return from 1 up to 4 evenly spaced values (data points) to give a buy/sell Recommendation
        # The returned data points are based on the regression line's data for future prices
        # Because we will avoid non-trading hours, checks must be conducted for EOD and non trading days

        mktCloseBase = datetime(year=2018, month=1, day=1, hour=16, minute=0, second=0)
        mktCloseOffset = timedelta(minutes=(self.timeInterval - 1))
        adjustedMktClose = (mktCloseBase - mktCloseOffset).time()
        mktClose = mktCloseBase.time() # 16:00 Eastern Standard Time (U.S.A.)
        predictBeginIndex = 100
        nextBusinessHour = CustomBusinessHour(start='8:30', end='16:00', calendar=USFederalHolidayCalendar())
        nextBusinessDay = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        validFutureTimePriceSet = []
        currentTimeStamp = self.timeStampList[predictBeginIndex - 1:]

        # Creates a list of future time stamps and prices ignoring closing hours, weekends, and holidays
        for timeStampIterator in range(0,121):
            if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
                currentTimeStamp += pandas.tseries.offsets.Minute(self.timeInterval)
                if currentTimeStamp.time > mktClose:
                    currentTimeStamp += nextBusinessHour
            else:
                currentTimeStamp += nextBusinessDay
            pricePrediction = self.linearModel.predict(predictBeginIndex + timeStampIterator)[0][0] # 2D array with one value
            validFutureTimePriceSet.append([currentTimeStamp[0].to_pydatetime(), pricePrediction])

        # Defines modulo value for intraday and index positions for daily api data
        if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
            moduloValue = 0
            if self.timeInterval == 1:
                moduloValue = 30 # Every 30 minutes or next day
            elif self.timeInterval == 5:
                moduloValue = 24 # Every 2 hours or next day
            else:
                moduloValue = 18 # Every 3 hours of next day
        else:
            presetIndexList = [0, 5, 10, 21] # Next day, next week, in two weeks, 30 days

        # Adds pre determined values to a dictionary based on the API interval and function selected
        presetTimeStampDict = {}
        timeFormat = '%a, %b %d %I:%M%p'
        for index, timeStamp in enumerate(validFutureTimePriceSet):
            currentTimeStamp = validFutureTimePriceSet[index][0]
            currentPrice = validFutureTimePriceSet[index][1]
            if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
                if currentTimeStamp.time() < adjustedMktClose:
                    if ((index % moduloValue) == 0 and (index != 0)):
                        presetTimeStampDict[currentTimeStamp.strftime(timeFormat)] = currentPrice
                else:
                    currentTimeStamp = validFutureTimePriceSet[index + 1][0]
                    presetTimeStampDict[currentTimeStamp.strftime(timeFormat)] = currentPrice
                    break
            else:
                for presetIndexValue in presetIndexList:
                    if presetIndexValue == index:
                        presetTimeStampDict[currentTimeStamp.strftime(timeFormat)] = currentPrice

        return presetTimeStampDict

class ColorizedText():

    def __init__(self, text):
        self.text = text

    def getColor(self):
        color = ''
        if self.text == 'BUY':
            color = 'green'
        else:
            color = 'red'

        return color

class UserSearchData():

    def __init__(self, text, interval, function):
        self.sanitizedSearchString = text.lower()
        self.sanitizedSearchString = ''.join(character for character in self.sanitizedSearchString if character.isalnum())
        self.apiLookupFunction = function

        # Formats the interval query used in the API url based hitting the intraday or daily API
        self.timeInterval = 1 #day
        if function == 'TIME_SERIES_INTRADAY':
            self.timeInterval = interval # API can return 1, 5, 15, 30, 60 min intervals

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
