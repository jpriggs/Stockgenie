import os
from datetime import datetime
from models import ApiStockData
import pandas as pd
import json
import requests

from flask import Flask, render_template, url_for, request, redirect, flash
#from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '\x16\x9a\xb8\xf9D\xba6\x0f\\\xf6\xac\x8dh\xb1\x92\x13\xcf\x18\xe27\x1c\x12\x19\xf9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'stockgenie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

def stockListSearch():
    stockDict = pd.read_csv('stocklist.csv').set_index('Symbol').T.to_dict('list')
    searchItem = request.args.get('search-item').lower()
    searchItem = ''.join(sub for sub in searchItem if sub.isalnum())
    formattedStockDict = {key.lower(): [value.lower().replace('.', '').replace(',', '').replace(' ', '').replace('-', '').replace('/', '') for value in values] for key, values in stockDict.items()}
    matchedItem = ''

    for key, value in formattedStockDict.items():
        if key == searchItem or value[0] == searchItem:
            matchedItem = key

    for key, value in stockDict.items():
        if key == matchedItem.upper():
            return [key, value[0], value[1]]

# Gets the external API
def getApiStockValues():

    apikey = 'Z0QNUSV1HF3JBMRR'
    function = 'TIME_SERIES_INTRADAY'
    symbol = stockListSearch()[0]
    minutes = 1
    interval = str(minutes) + 'min'
    outputsize = 'compact'
    datatype = 'json'
    url = 'https://www.alphavantage.co/query?function={}&symbol={}&interval={}&outputsize={}&datatype={}&apikey={}'.format(function, symbol, interval, outputsize, datatype, apikey)
    #https://www.alphavantage.co/documentation/
    #https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=demo

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
        stockHistoricalPrices = [ApiStockData(x, timeStampValue[x]['4. close']) for x in timeStampData]

        # Iterates through the sorted data and displays the timestamp and closing prices
        for obj in sorted(stockHistoricalPrices, key=lambda sortObjectIteration: sortObjectIteration.timeStampValue, reverse=False):
            print('{}: {}'.format(obj.timeStampValue, obj.priceValue))

# Views
@app.route('/')
@app.route('/index')
def index():

    data = stockListSearch()
    getApiStockValues()
    print(data)
    stockData = dict({
                'Name': '{}'.format(stockListSearch()[1]),
                'Symbol': '{}'.format(stockListSearch()[0]),
                'Exchange': '{}'.format(stockListSearch()[2])
    })


    return render_template('base.html', stockData=stockData)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
