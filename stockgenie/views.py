import os
from datetime import datetime
import pandas as pd
import json
import requests
import plotly
import plotly.graph_objs as go
import numpy as np
from sklearn import datasets, linear_model

from flask import Flask, render_template, url_for, request, redirect, flash
from models import ApiStockData, UserSearchData, StockListData
#from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#app.config['SECRET_KEY'] = '\x16\x9a\xb8\xf9D\xba6\x0f\\\xf6\xac\x8dh\xb1\x92\x13\xcf\x18\xe27\x1c\x12\x19\xf9'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'stockgenie.db')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)


def stockPriceChart(dataset, name):

    # Load the dataset
    companyName = name
    ds = dataset
    data = [go.Scatter(x=ds.index, y=ds.Price)]
    config = {'displayModeBar': False}
    layout = go.Layout(
        title=companyName + 'Price History',
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

def stockListSearch():
    # Sends the user input to a constructor class and formats the string
    searchString = request.args.get('search-item')
    if searchString is None or searchString is '':
        print ("Search String Error")
        return None
    searchString = UserSearchData(searchString)

    # Formats the stock list dictionary to match any user input
    stockList = {}
    unformattedDictSymbol = ''
    stockListDict = pd.read_csv('stocklist.csv').set_index('Symbol').T.to_dict('list')
    for key, value in stockListDict.items():
        stockValues = StockListData(key, value[0], value[1])

        if stockValues.stockSymbol == searchString.searchData:
            unformattedDictSymbol = key
        stockList.update({stockValues.stockSymbol: [stockValues.companyName, stockValues.stockExchange]})

    if stockList is None or stockList == {} or unformattedDictSymbol is '':
        print('StockList Dictionary Error')
        return None

    # Searches the stock list to match the user imput string and returns the matching key
    matchedItem = ''
    for key, value in stockList.items():
        if key == searchString.searchData or value[0] == searchString.searchData:
            matchedItem = unformattedDictSymbol
    if matchedItem is None or matchedItem is '':
        print ('Dictionary matching error')
        return None

    # Uses the user matched key to return the unformatted dictionary values
    searchResults = []
    for key, value in stockListDict.items():
        if key == matchedItem:
            searchResults = [key.replace('^', '-'), value[0], value[1]]

    if searchResults is None or searchResults is [] or '^' in searchResults[0]:
        print ('No returned values to function')
        return None

    return searchResults

# Get's the basic stock info from the Google Finance API
def getBasicStockInfo(symbol, name, exchange):
    stockSymbol = symbol
    companyName = name
    stockExchange = exchange
    datatype = 'json'
    url = 'https://finance.google.com/finance?q={}&output={}'.format(stockSymbol, datatype)

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
                            'Updated': '{}'.format(datetime.now().strftime('%b %d, %Y %H:%M:%S'))
            })
    except:
        stockData = dict({
                        'Name': '{}'.format(companyName),
                        'Symbol': '{}'.format(stockSymbol),
                        'Exchange': '{}'.format(stockExchange),
                        'Price': 'N/A',
                        'Open': 'N/A',
                        '$ Chg': 'N/A',
                        '% Chg': 'N/A',
                        'High': 'N/A',
                        'Low': 'N/A',
                        'MktCap': 'N/A',
                        'P/E Ratio': 'N/A',
                        'Beta': 'N/A',
                        'EPS': 'N/A',
                        '52w High': 'N/A',
                        '52w Low': 'N/A',
                        'Shares': 'N/A',
                        'Updated': '{}'.format(datetime.now().strftime('%b %d, %Y %H:%M:%S'))
        })
    # Checks if the API returns a JSON object
    if stockData is None or stockData is {}:
        return None

    return stockData

# Gets the external API
def getApiStockValues(symbol):

    apikey = 'Z0QNUSV1HF3JBMRR'
    function = 'TIME_SERIES_INTRADAY'
    stockSymbol = symbol
    minutes = 1
    interval = str(minutes) + 'min'
    outputsize = 'compact'
    datatype = 'json'
    url = 'https://www.alphavantage.co/query?function={}&symbol={}&interval={}&outputsize={}&datatype={}&apikey={}'.format(function, stockSymbol, interval, outputsize, datatype, apikey)
    #https://www.alphavantage.co/documentation/
    #https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=demo
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
            stockHistoricalPrices = [ApiStockData(key, timeStampData[key]['4. close']) for key in timeStampData]

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
    stockMatchResult = stockListSearch()
    symbol = stockMatchResult[0]
    name = stockMatchResult[1]
    exchange = stockMatchResult[2]

    # Validates that a user inputted matched stock is returned
    if stockMatchResult is None:
        return render_template('base.html')

    # Gets API values from Alphavantage (pricing) and Google Finance (Stock Info)
    pricingData = getApiStockValues(symbol)
    if pricingData is None:
        return render_template('base.html')

    stockData =  getBasicStockInfo(symbol, name, exchange)
    if stockData is None:
        return render_template('base.html')

    # Creates a chart based on the price data returned from the API
    if stockData is None:
        companyName = name
    companyName = stockData['Name'][:38]
    chart = stockPriceChart(pricingData, companyName)

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
