import json
import requests
from datetime import datetime, time, timedelta
import numpy as np
from sklearn import linear_model
from pandas.tseries.offsets import CustomBusinessHour, CustomBusinessDay, Minute
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

        self.linearModel = linear_model.LinearRegression()
        self.times = np.reshape(self.timeStampValue, (len(self.timeStampValue), 1))
        self.prices = np.reshape(dataset.Price, (len(dataset.Price), 1))
        self.linearModel.fit(self.times, self.prices)

    def calculateRegressionLine(self):

        # Create linear model data
        linearFitPricesMatrix = self.linearModel.predict(self.times)
        regressionLineData = [column for row in linearFitPricesMatrix for column in row]
        return regressionLineData

    def calculatePricePrediction(self):
        self.timeInterval = 1 #temp value!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        mktCloseBase = datetime(year=2018, month=1, day=1, hour=16, minute=0, second=0)
        mktCloseOffset = timedelta(minutes=(self.timeInterval - 1))
        adjustedMktClose = (mktCloseBase - mktCloseOffset).time()
        mktClose = mktCloseBase.time() # 16:00 Eastern Standard Time (U.S.A.)
        predictBeginIndex = 100
        nextBusinessHour = CustomBusinessHour(start='8:30', end='16:00', calendar=USFederalHolidayCalendar())
        nextBusinessDay = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        validFutureTimePriceSet = []
        currentTimeStamp = self.timeStampList[99:]

        # Creates a list of future time stamps and prices ignoring closing hours, weekends, and holidays
        for timeStampIterator in range(0,121):
            if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
                currentTimeStamp += Minute(self.timeInterval) #self.timeInterval
                if currentTimeStamp.time > mktClose:
                    currentTimeStamp += nextBusinessHour
            else:
                currentTimeStamp += nextBusinessDay
            pricePredictionMatrix = self.linearModel.predict(predictBeginIndex + timeStampIterator)
            pricePrediction = pricePredictionMatrix[0][0] # 2D array with one value
            validFutureTimePriceSet.append([currentTimeStamp[0].to_pydatetime(), pricePrediction])

        # Adds pre determined values to a dictionary based on the API interval selected
        returnValues = {}
        if self.apiLookupFunction == 'TIME_SERIES_INTRADAY':
            for index, timeStamp in enumerate(validFutureTimePriceSet):
                if validFutureTimePriceSet[index][0].time() < adjustedMktClose:
                    # Adds 30 min, 1 hour, 1.5 hours, and 2 hours to dictionary if in range of look ahead, or next day if not
                    if self.timeInterval == 1:
                        if ((index % 30) == 0) and (index != 0):
                            keyFormat = validFutureTimePriceSet[index][0].strftime('%a, %b %d %I:%M%p')
                            returnValues[keyFormat] = validFutureTimePriceSet[index][1]
                    # Adds 2 hours, 4 hours, and 6 hours to dictionary if in range of look ahead, or next day if not
                    if self.timeInterval == 5:
                        if ((index % 24) == 0) and (index != 0):
                            keyFormat = validFutureTimePriceSet[index][0].strftime('%a, %b %d %I:%M%p')
                            returnValues[keyFormat] = validFutureTimePriceSet[index][1]
                    # Adds 3 hours and 6 hours to dictionary if in range of look ahead, or next day if not
                    if self.timeInterval == 10:
                        if ((index % 18) == 0) and (index != 0):
                            keyFormat = validFutureTimePriceSet[index][0].strftime('%a, %b %d %I:%M%p')
                            returnValues[keyFormat] = validFutureTimePriceSet[index][1]
                else:
                    keyFormat = validFutureTimePriceSet[index + 1][0].strftime('%a, %b %d %I:%M%p')
                    returnValues[keyFormat] = validFutureTimePriceSet[index][1]
                    break
                print(index, timeStamp[0], timeStamp[1])
            print(returnValues)
        else:
            for index, timeStamp in enumerate(validFutureTimePriceSet):
                if index == 0 or index == 5 or index == 10 or index == 21:
                    keyFormat = validFutureTimePriceSet[index][0].strftime('%a, %b %d, %Y')
                    returnValues[keyFormat] = validFutureTimePriceSet[index][1]
                #print(index, timeStamp[0], timeStamp[1])
            #print(returnValues)

        return returnValues

class ColorizeText():

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
