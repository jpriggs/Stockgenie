import os
from datetime import datetime
import pandas as pd
import json
import requests
import plotly
import plotly.graph_objs as go

from flask import Flask, render_template, url_for, request, redirect, flash
from models import ApiStockData, Regression, UserSearchData, StockListData, ColorizeText

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

def createStockPriceChart(dataset, name, regression):

    # Loads the price data, time series data, and regression line data into the chart
    priceHistoryLine = go.Scatter(x=dataset.index, y=dataset.Price, name='Price History', line=dict(color='#3030DB', width=3))
    regressionLine = go.Scatter(x=dataset.index, y=regression, name='Regression', line=dict(color='#CC2446', width=3))
    config = {'displayModeBar': False}
    layout = go.Layout(
        title=name,
        titlefont=dict(
            family='Helvetica, sans-serif',
            size=20,
            color='#000'
        ),
        showlegend=True,
        legend=dict(orientation='v', xanchor='auto', yanchor='bottom'),
        margin=go.Margin(
            l=85,
            r=35,
            b=50,
            t=50,
            pad=0
        ),
        xaxis=dict(
            title='Time',
            titlefont=dict(
                family='Arial Black, sans-serif',
                size=18,
                color='#0066ff'
            ),
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=True,
            autotick=True,
            showticklabels=True
        ),
        yaxis=dict(
            title='Price',
            titlefont=dict(
                family='Arial Black, sans-serif',
                size=18,
                color='#006600'
            ),
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=True,
            autotick=True,
            tickformat='$,.2f',
            showticklabels=True,
            tickangle=45
        )
    )
    data = [priceHistoryLine, regressionLine]
    fig = dict(data=data, layout=layout)

    return plotly.offline.plot(fig, config=config, output_type='div', show_link=False, link_text=False)

def stockListSearch(searchString):

    # Ensures a search string has been entered into the function
    if not searchString:
        print ("searchString error")
        return None

    # Loads and sanitizes the stock dictionary to match any user input
    rawStockSymbol = ''
    rawStocksDict = pd.read_csv('stocklist.csv').set_index('Symbol').T.to_dict('list')
    for thisStockSymbol, thisStockData in rawStocksDict.items():
        #thisStockData contains [stock name, exchange name]
        stockValues = StockListData(thisStockSymbol, thisStockData[0], thisStockData[1])

        # Checks if the user search string matches stock symbol or company name in the dictionary
        if stockValues.matchesNameOrSymbol(searchString):
            return stockValues

    print ('Error:\tNo returned values to function')
    return None

# Get's the basic stock info from the Google Finance API
def getBasicStockInfo(symbol, name, exchange):
    dateTimeFormat = '%b %d, %Y %H:%M:%S'
    datatype = 'json'
    url = 'https://finance.google.com/finance?q={}&output={}'.format(symbol, datatype)

    try:
        response = requests.get(url)
        if response.status_code in (200,):
            data = json.loads(response.content[6:-2].decode('unicode_escape'))
            stockData = dict({
                            'Name': data['name'],
                            'Symbol': data['t'],
                            'Exchange': data['e'],
                            'Price': data['l'],
                            'Open': data['op'],
                            '$ Chg': data['c'],
                            '% Chg': data['cp'],
                            'High': data['hi'],
                            'Low': data['lo'],
                            'MktCap': data['mc'],
                            'P/E Ratio': data['pe'],
                            'Beta': data['beta'],
                            'EPS': data['eps'],
                            '52w High': data['hi52'],
                            '52w Low': data['lo52'],
                            'Shares': data['shares'],
                            'Updated': '{}'.format(datetime.now().strftime(dateTimeFormat))
            })
    except:
        stockData = dict({
                        'Name': '{}'.format(name),
                        'Symbol': '{}'.format(symbol),
                        'Exchange': '{}'.format(exchange),
                        'Price': 'n/a',
                        'Open': 'n/a',
                        '$ Chg': 'n/a',
                        '% Chg': 'n/a',
                        'High': 'n/a',
                        'Low': 'n/a',
                        'MktCap': 'n/a',
                        'P/E Ratio': 'n/a',
                        'Beta': 'n/a',
                        'EPS': 'n/a',
                        '52w High': 'n/a',
                        '52w Low': 'n/a',
                        'Shares': 'n/a',
                        'Updated': '{}'.format(datetime.now().strftime(dateTimeFormat))
        })

    # Checks if the API returns a JSON object
    if not stockData:
        return None

    return stockData

# Gets the external stock price API
def getApiStockValues(symbol, searchData):

    apiPriceKey = '4. close'
    apikey = 'Z0QNUSV1HF3JBMRR'
    outputsize = 'compact'
    datatype = 'json'
    urlBase = 'https://www.alphavantage.co/query?function={}&symbol={}&outputsize={}&datatype={}&apikey={}{}'

    # Get the response data from either of the two relevant APIs
    response = None
    jsonApiObject = None
    try:
        intervalStr = '&interval=' + (str(searchData.timeInterval) + 'min') if searchData.apiLookupFunction == 'TIME_SERIES_INTRADAY' else ''
        response = requests.get(urlBase.format(searchData.apiLookupFunction, symbol, outputsize, datatype, apikey, intervalStr))
        if response.status_code in (200,):
            jsonApiObject = json.loads(response.content.decode('unicode_escape'))
        if 'Error Message' in jsonApiObject:
            jsonApiObject = None
            raise ValueError
    except ValueError:
        searchData.switchLookupFunction()
        intervalStr = '&interval=' + (str(searchData.timeInterval) + 'min') if searchData.apiLookupFunction == 'TIME_SERIES_INTRADAY' else ''
        response = requests.get(urlBase.format(searchData.apiLookupFunction, symbol, outputsize, datatype, apikey, intervalStr))
        if response.status_code in (200,):
            jsonApiObject = json.loads(response.content.decode('unicode_escape'))
        if 'Error Message' in jsonApiObject:
            return None
    except:
        return None

    # Ensures that API data has been returned
    if jsonApiObject is None:
        return None

    # Adds and sorts the API data from oldest to newest data points
    timeStampData = jsonApiObject[list(jsonApiObject)[1]]
    stockHistoricalPrices = []
    for timeStampValue in timeStampData:
        priceValue = timeStampData[timeStampValue][apiPriceKey]
        # Instantiates the ApiStockData class passing in timestamp and price values based on an intraday or daily time series
        apiStockDataObject = ApiStockData(timeStampValue, priceValue, searchData.apiLookupFunction)
        stockHistoricalPrices.insert(0, [apiStockDataObject.timeStampValue, apiStockDataObject.priceValue])

    # Creates a dataframe from the timestamps and prices using Pandas
    labels = ['Timestamp', 'Price']
    df = pd.DataFrame.from_records(stockHistoricalPrices, columns=labels, index='Timestamp')

    return df

# Views
@app.route('/')
@app.route('/index')
def index():
    userSearchedStock = request.args.get('search-item')
    userInterval = 1 # in minutes - temp value
    userFunction = 'TIME_SERIES_INTRADAY' # TIME_SERIES_INTRADAY or TIME_SERIES_DAILY - temp value
    if not userSearchedStock:
        return render_template('base.html')

    # Instantiates the user search inputted values class
    userInputSearchValues = UserSearchData(userSearchedStock, userInterval, userFunction)

    # Gets the user matched stock result
    stockMatchResult = stockListSearch(userInputSearchValues.sanitizedSearchString)
    if stockMatchResult is None:
        return render_template('base.html')
    stockMatchDataContainer = StockListData(stockMatchResult.stockSymbol, stockMatchResult.companyName, stockMatchResult.stockExchange)

    # Gets API values from Alphavantage (pricing) and Google Finance (Stock Info)
    timeSeriesPriceData = getApiStockValues(stockMatchDataContainer.getApiSafeSymbol(stockMatchResult.stockSymbol), userInputSearchValues)
    if timeSeriesPriceData is None:
        return render_template('base.html')

    stockData =  getBasicStockInfo(stockMatchDataContainer.getApiSafeSymbol(stockMatchResult.stockSymbol), stockMatchDataContainer.companyName, stockMatchDataContainer.stockExchange)
    if stockData is None:
        return render_template('base.html')

    # Generate regression data
    regressionData = Regression(timeSeriesPriceData, userInputSearchValues.timeInterval, userInputSearchValues.apiLookupFunction)
    regressionLine = regressionData.calculateRegressionLine()
    predictData = regressionData.calculatePricePrediction()

    # Prototype prediction recommendation based on current price and predicted price
    latestPredictData = list(predictData.items())[-1] # Get the last element in the prediction dictionary
    recommendation = {'Recommendation': 'BUY' if timeSeriesPriceData.Price[99] < latestPredictData[1] else 'SELL'}
    colorizeObjectData = ColorizeText(recommendation['Recommendation'])
    recommendColor = colorizeObjectData.getColor()

    # Creates a chart based on the price data returned from the API
    chart = createStockPriceChart(timeSeriesPriceData, stockMatchDataContainer.companyName, regressionLine)

    return render_template('base.html', stockData=stockData, chart=chart, predictData=predictData, recommendation=recommendation, recommendColor=recommendColor)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
