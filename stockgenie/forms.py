from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired
import csv

class StockForm(Form):

    stockSearch = StringField('Enter a stock symbol or name', validators=[DataRequired()])

    def validate(self):
        if not Form.validate(self):
            return False

        return True
