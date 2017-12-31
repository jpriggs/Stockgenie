#Data Loader
import os
from numpy import genfromtxt
from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import csv
import pandas as pd

basedir = os.path.abspath(os.path.dirname(__file__))
Base = declarative_base()

# Declare the database and it's columns
class Stock(Base):
    __tablename__ = 'stock_list'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True, nullable=False)
    exchange = Column(VARCHAR(4), nullable=False)
    symbol = Column(VARCHAR(6), unique=True, nullable=False)
    name = Column(VARCHAR(80), nullable=False)
    sector = Column(VARCHAR(40))
    industry = Column(VARCHAR(40))

# Create the database
engine = create_engine('sqlite:///' + os.path.join(basedir, 'stockgenie.db'))
Base.metadata.create_all(engine)

# Load the csv file and inserts it into the database
file_name = 'stocks.csv'
df = pd.read_csv(file_name)
df.to_sql(con=engine, index_label='id', name=Stock.__tablename__, if_exists='replace')
