import json
import requests
from datetime import datetime
datetime.strftime
#from sqlalchemy import desc
#from stockgenie import db

class ApiStockData():

    def __init__(self, timeStamp, price):
        self.timeStampValue = timeStamp
        self.priceValue = price

#class Stock():

    #def stockAPIData():

        # Google variables
        #symbol = 'NFLX'
        #interval = str(60) # in seconds
        #days = 1
        #period = str(days) # in days
        #functions = 'd,o,h,c,v'
        #dataformat = 'cpct'
        #datatype = 'json'
        #timestamp = 0.0
        #timeValue = datetime.fromtimestamp(timestamp)
        #url = 'https://finance.google.com/finance/getprices?i=' + interval + '&p=' + period + 'd' + '&f=' + functions + '&df=' + dataformat + '&q=' + symbol
        #testUrl = 'https://finance.google.com/finance?q=NFLX&ouput=json'

        #response = requests.get(testUrl)
        #if response.status_code in (200,):
            #finData = json.loads(response.content[6:-2].decode('unicode_escape'))

            #stockData = dict({
                            #'Name': '{}'.format(finData['name']),
                            #'Symbol': '{}'.format(finData['t']),
                            #'Exchange': '{}'.format(finData['e']),
                            #'Price': '{}'.format(finData['l']),
                            #'Open': '{}'.format(finData['op']),
                            #'PriceChg': '{}'.format(finData['c']),
                            #'PercentChg': '{}%'.format(finData['cp']),
                            #'High': '{}'.format(finData['hi']),
                            #'Low': '{}'.format(finData['lo']),
                            #'MktCap': '{}'.format(finData['mc']),
                            #'P/E Ratio': '{}'.format(finData['pe']),
                            #'Beta': '{}'.format(finData['beta']),
                            #'EPS': '{}'.format(finData['eps']),
                            #'52w High': '{}'.format(finData['hi52']),
                            #'52w Low': '{}'.format(finData['lo52']),
                            #'Shares': '{}'.format(finData['shares']),
                            #'Updated': '{}'.format(datetime.now().strftime('%b %d, %Y %H:%M:%S'))
            #})

        #return stockData

# class User(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(80), unique=True, nullable=False)
    #email = db.Column(db.String(120), unique=True, nullable=False)
    #cash_balance = db.Column(db.Float(13, 4), nullable=False)

    #def __repr__(self):
        #return '<user %r>' % self.username
