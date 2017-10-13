# FinanceWebApp

https://docs.google.com/document/d/1g--eq2kioE2OUg1vGMcvMv8Kbggge3l0mlDkEN_3JHo/edit?usp=sharing

**Goal:** Create a webapp that pulls in .csv/api financial data of stock price history and creates a regression analysis to help create a simple machine learning tool that tries to guess a future stock price.

**Required Tools:**
- Heroku’s DB - Postgres
- HTML/CSS/JS - Front End
- Python - Back End

**Sprints:**
- Week 1: Setup relational database tables (Postgres)
- Week 2: Design website look and feel (HTML/CSS/JS)
- Week3-4: Implement functionality (Python 3)

**Webapp details:**
Stock symbol lookup, create a regression analysis of intraday stock price changes, a simple machine learning algorithm attempts to guess the next stock price based on historical data, measures the difference between actual price and estimated price and adjusts its next guess based on a standard deviation model? Asynchronous updating on each stock fetching interval.

**Resources:**
Data Location:
Google’s API:
https://www.google.com/finance/getprices?i=[PERIOD]&p=[DAYS]d&f=d,o,h,l,c,v&df=cpct&q=[TICKER]
