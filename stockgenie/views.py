import os
from datetime import datetime
import pandas as pd
import json
import requests
import plotly
import plotly.graph_objs as go
import numpy as np
import matplotlib.dates as mdates
from scipy import stats

from flask import Flask, render_template, url_for, request, redirect, flash
from models import ApiStockData, UserSearchData, StockListData

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

def createStockPriceChart(dataset, name):

    # Load the dataset
    data = [go.Scatter(x=dataset.index, y=dataset.Price)]
    config = {'displayModeBar': False}
    layout = go.Layout(
        title=name + ' Price History',
        titlefont=dict(
            family='Helvetica, sans-serif',
            size=20,
            color='#000'
        ),
        showlegend=False,
        margin=go.Margin(
            l=85,
            r=35,
            b=50,
            t=50,
            pad=2
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
    fig = go.Figure(data=data, layout=layout)

    return plotly.offline.plot(fig, config=config, output_type='div', show_link=False, link_text=False)

def stockListSearch(searchString):

    # Ensures a search string has been entered into the function
    if not searchString:
        print ("searchString error")
        return None
    searchDataContainer = UserSearchData(searchString)

    # Loads and sanitizes the stock dictionary to match any user input
    rawStockSymbol = ''
    rawStocksDict = pd.read_csv('stocklist.csv').set_index('Symbol').T.to_dict('list')
    for thisStockSymbol, thisStockData in rawStocksDict.items():
        #thisStockData contains [stock name, exchange name]
        stockValues = StockListData(thisStockSymbol, thisStockData[0], thisStockData[1])
        # Checks if the user search string matches stock symbol or company name in the dictionary
        if stockValues.matchesNameOrSymbol(searchDataContainer.sanitizedSearchString):
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
                            'Name': '{}'.format(data['name']),
                            'Symbol': '{}'.format(data['t']),
                            'Exchange': '{}'.format(data['e']),
                            'Price': '{}'.format(data['l']),
                            'Open': '{}'.format(data['op']),
                            '$ Chg': '{}'.format(data['c']),
                            '% Chg': '{}%'.format(data['cp']),
                            'High': '{}'.format(data['hi']),
                            'Low': '{}'.format(data['lo']),
                            'MktCap': '{}'.format(data['mc']),
                            'P/E Ratio': '{}'.format(data['pe']),
                            'Beta': '{}'.format(data['beta']),
                            'EPS': '{}'.format(data['eps']),
                            '52w High': '{}'.format(data['hi52']),
                            '52w Low': '{}'.format(data['lo52']),
                            'Shares': '{}'.format(data['shares']),
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
def getApiStockValues(symbol):

    apiPriceKey = '4. close'
    apikey = 'Z0QNUSV1HF3JBMRR'
    function = 'TIME_SERIES_INTRADAY'
    minutes = 1
    interval = str(minutes) + 'min'
    outputsize = 'compact'
    datatype = 'json'
    url = 'https://www.alphavantage.co/query?function={}&symbol={}&interval={}&outputsize={}&datatype={}&apikey={}'.format(function, symbol, interval, outputsize, datatype, apikey)

    try:
        response = requests.get(url)
        if response.status_code in (200,):
            pricingData = json.loads(response.content.decode('unicode_escape'))
            timeStampData = pricingData[list(pricingData)[1]]

            # Adds timestamp values as indexes and all close price values to a list
            stockHistoricalPrices = []
            for timeStampValue in timeStampData:
                priceValue = timeStampData[timeStampValue]['4. close']
                stockHistoricalPrices.append(ApiStockData(timeStampValue, priceValue))

            # Adds objects from a class constructor to a list
            stockHistoricalPrices = [ApiStockData(timeStampKey, timeStampData[timeStampKey][apiPriceKey]) for timeStampKey in timeStampData]

            stockTimeSeriesDataset = []
            labels = ['Time', 'Price']
            # Iterates through the sorted data and displays the timestamp and closing prices
            for obj in sorted(stockHistoricalPrices, key=lambda sortObjectIteration: sortObjectIteration.timeStampValue, reverse=False):
                stockTimeSeriesDataset.append([obj.timeStampValue, obj.priceValue])

            # Creates a dataframe using Pandas
            df = pd.DataFrame.from_records(stockTimeSeriesDataset, columns=labels, index='Time')

            return df
    except:
        return None

# Views
@app.route('/')
@app.route('/index')
def index():
    userSearchedStock = request.args.get('search-item')
    if not userSearchedStock:
        return render_template('base.html')

    stockMatchResult = stockListSearch(userSearchedStock)
    # Validates that a user inputted matched stock is returned
    if stockMatchResult is None:
        return render_template('base.html')
    stockMatchDataContainer = StockListData(stockMatchResult.stockSymbol, stockMatchResult.companyName, stockMatchResult.stockExchange)

    # Gets API values from Alphavantage (pricing) and Google Finance (Stock Info)
    pricingData = getApiStockValues(stockMatchDataContainer.replaceCaretSymbol(stockMatchResult.stockSymbol))
    if pricingData is None:
        return render_template('base.html')
    stockData =  getBasicStockInfo(stockMatchDataContainer.replaceCaretSymbol(stockMatchResult.stockSymbol), stockMatchDataContainer.companyName, stockMatchDataContainer.stockExchange)
    if stockData is None:
        return render_template('base.html')

    # Adjusts the chart title length to fit the chart size
    baseTitleLength = 32
    for character in stockMatchDataContainer.companyName[baseTitleLength:]:
        print(len(stockMatchDataContainer.companyName[:baseTitleLength]), stockMatchDataContainer.companyName[:baseTitleLength])
        if stockMatchDataContainer.companyName[baseTitleLength - 1:baseTitleLength] is not ' ':
            baseTitleLength += 1
        else:
            baseTitleLength -= 1
            break

    # Creates a chart based on the price data returned from the API
    chart = createStockPriceChart(pricingData, stockMatchDataContainer.companyName[:baseTitleLength])

    return render_template('base.html', stockData=stockData, chart=chart)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
