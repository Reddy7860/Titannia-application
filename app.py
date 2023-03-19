from flask import render_template,flash,request, url_for, redirect,Flask,redirect, Response, session,jsonify
from datetime import datetime
import requests
import json
import pandas as pd
import numpy as np
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import math
from pytz import timezone 
from datetime import timedelta, date
from google.oauth2 import service_account
import pandas_gbq
import plotly
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
from get_vix_data import get_vix_data
from get_global_market import get_global_market
from get_client_orders import get_display_data
from get_combined_chart import get_combined_chart
from options_greek import long_call,long_put,short_call,short_put,binary_call,binary_put,bull_spread,bear_spread,straddle,risk_reversal,strangle,butterfly_spread,strip
from nsepy import get_history
import yfinance as yf
from bs4 import BeautifulSoup
from pandas.tseries.offsets import BDay

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set secret key for session management
app.secret_key = "mysecretkey"
# Set up MongoDB URIs
mongo_user = os.environ.get('MONGO_USER')
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_uri_db1 = os.environ.get('MONGO_URI_DB1')
mongo_uri_db2 = os.environ.get('MONGO_URI_DB2')

app.config["MONGO_URI_DB1"] = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_uri_db1}"
app.config["MONGO_URI_DB2"] = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_uri_db2}"

mongo_db1 = PyMongo(app, uri=app.config["MONGO_URI_DB1"])
db = mongo_db1.db

mongo_db2 = PyMongo(app, uri=app.config["MONGO_URI_DB2"])
db2 = mongo_db2.db

# Set the path to the JSON key file
key_path = 'static/ferrous-module-376519-7e08f583402d.json'
# Load the credentials from the JSON key file
credentials = service_account.Credentials.from_service_account_file(key_path)
# Set the environment variable for the credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path




# Create a list of users for demo purposes
users = [
    {"email": "admin@gmail.com", "password": "admin"},
    {"email": "user1@gmail.com", "password": "user1"},
    {"email": "user2@gmail.com", "password": "user2"}
]

# Function to check if a user exists and the password is correct
def authenticate_user(email, password):
    for user in users:
        if user["email"] == email and user["password"] == password:
            return True
    return False

@app.route('/')
def index():
    now = datetime.now()
    if "email" in session:
        return redirect(url_for('login_view'))
    return render_template('index.html', now=now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if authenticate_user(email, password):
            session["email"] = email
            return redirect(url_for('login_view'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')
    

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login_view', methods=['GET', 'POST'])
def login_view():
    if "email" not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        stock_input = request.form['stock_input']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # Do something with the form data
        return render_template('login_view.html', stock_input=stock_input, start_date=start_date, end_date=end_date)
    else:
        # NSE_List = pd.read_csv("application/NSE_Stocks_List.csv")
        # NSE_Tickers = NSE_List['Yahoo Symbol'].tolist()
        NSE_Tickers = ['RELIANCE.NS','SBIN.NS','HDFCBANK.NS']
        return render_template('login_view.html',tickers=NSE_Tickers)
@app.route('/new_link', methods=['GET', 'POST'])
def new_link():
    if request.method == 'POST':
        # get form data from request object
        link_url = request.form['link_url']
        link_title = request.form['link_title']
        
        # save the link to the database or perform other actions as needed
        
        # redirect the user to the home page
        return redirect(url_for('home'))
    else:
        # render the new link form template
        return render_template('new_link.html')

@app.route('/contact', methods = ['GET', 'POST'])  
def contact():  
   form = ContactForm()  
   if form.validate() == False:  
      flash('All fields are required.')  
   return render_template('contact.html', form = form) 

@app.route('/about', methods = ['GET', 'POST'])  
def about():  
   form = aboutForm()  
   if form.validate() == False:  
      flash('All fields are required.')  
   return render_template('about.html', form = form) 

@app.route('/company_overview',methods=['GET', 'POST'])
def company_overview():
    if request.method == 'POST':
        stock_input = request.form['stock_input']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # Do something with the form data
        return render_template('company_overview.html', stock_input=stock_input, start_date=start_date, end_date=end_date)
    else:
        # NSE_List = pd.read_csv("application/NSE_Stocks_List.csv")
        # NSE_Tickers = NSE_List['Yahoo Symbol'].tolist()

        NSE_Tickers = ['RELIANCE.NS','SBIN.NS','WIPRO.NS','HDFCBANK.NS']
        return render_template('company_overview.html',tickers=NSE_Tickers)

# Handle the AJAX request and return the updated infobox content
@app.route("/get_infobox_data", methods=['POST'])
def get_infobox_data():

    tabName = request.get_json()["tabName"]
    print(tabName)
    selected_stock = request.get_json()["selected_stock"]
    print(selected_stock)

    if tabName == "#valuation":

        money_control_data = pd.read_csv("Money_Control_Tickers.csv")
        row_number = np.where(money_control_data['Company'].str.contains(selected_stock))[0][0]
        money_control_url = "https://priceapi.moneycontrol.com/pricefeed/nse/equitycash/" + money_control_data.iloc[row_number, 4]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(money_control_url, headers=headers)
        stocks_valuation = response.json()
        return jsonify(valuation_info=stocks_valuation,tabName=tabName)
    elif tabName == "#price_and_returns":
        data = yf.download(selected_stock, start="2022-03-01", end="2023-03-01")
        # Compute moving averages
        data['mm10'] = data['Close'].rolling(window=10).mean()
        data['mm30'] = data['Close'].rolling(window=30).mean()

        data = data.round(2)
        # Create a subplot with two y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add volume bar chart
        fig.add_trace(
            go.Bar(x=data.index, y=data['Volume'], name="Volume"),
            secondary_y=False,
        )

        # Add price line chart
        fig.add_trace(
            go.Scatter(x=data.index, y=data['Adj Close'], name="Price"),
            secondary_y=True,
        )

        # Add moving averages line charts
        fig.add_trace(
            go.Scatter(x=data.index, y=data['mm10'], name="Weekly Moving Average"),
            secondary_y=True,
        )

        fig.add_trace(
            go.Scatter(x=data.index, y=data['mm30'], name="Monthly Moving Average"),
            secondary_y=True,
        )

        # Update layout and axis titles
        fig.update_layout(
            title=str(selected_stock) + ' Stock Data',
            xaxis_title="Date",
            yaxis_title="Volume",
            yaxis2_title="Price",
            legend=dict(x=0, y=1.1, orientation='h')
        )
        # Convert the figure to HTML and return as a JSON object
        html_fig = pio.to_html(fig, full_html=False)

        # Create the stock returns plot
        stock_ret = pd.DataFrame({'Date': data.index[1:], 'Adjusted': (data['Close'].apply(lambda x: math.log(x)) - data['Close'].apply(lambda x: math.log(x)).shift(1)).values[1:]})
        fig2 = go.Figure(data=[go.Scatter(x=stock_ret['Date'], y=stock_ret['Adjusted'])])
        fig2.update_layout(title=str(selected_stock)+" Returns", xaxis_title="Date", yaxis_title="Returns")
        html_fig2 = pio.to_html(fig2, full_html=False)

        return jsonify(html= html_fig, stock_returns=html_fig2,tabName=tabName)
    elif tabName == "#historic_data":
        # Fetch data from Yahoo Finance and remove missing values
        ticker = selected_stock
        start_date = "2022-03-03"
        end_date = "2023-03-01"
        df = yf.download(ticker, start=start_date, end=end_date)
        df.dropna(inplace=True)
        df = df.reset_index()
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        data = df
        # calculate the candle body and shadows
        data['body'] = abs(data['Close'] - data['Open'])
        data['upper_shadow'] = data[['Open', 'Close']].max(axis=1) - data['High']
        data['lower_shadow'] = data['Low'] - data[['Open', 'Close']].min(axis=1)
        data['Target'] = ''
        data['Entry'] = ''
        data['Stoploss'] = ''
        data['Signal'] = ''
        data['pattern'] = ''

        # identify patterns
        for i in range(len(data)):
            if i < 2:
                continue

            # Bullish Engulfing Pattern
            if data.loc[i-1, 'Close'] < data.loc[i-1, 'Open'] and data.loc[i, 'Close'] > data.loc[i, 'Open'] and data.loc[i, 'Close'] > data.loc[i-1, 'Open'] and data.loc[i, 'Open'] < data.loc[i-1, 'Close']:
                data.loc[i,"pattern"] = "Bullish Engulfing"
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price + (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'Low']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Buy'

            # Bearish Engulfing Pattern
            elif data.loc[i-1, 'Close'] > data.loc[i-1, 'Open'] and data.loc[i, 'Close'] < data.loc[i, 'Open'] and data.loc[i, 'Close'] < data.loc[i-1, 'Open'] and data.loc[i, 'Open'] > data.loc[i-1, 'Close']:
                data.loc[i,"pattern"] = "Bearish Engulfing"
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price - (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'High']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Sell'

            # Doji
            elif data.loc[i, 'body'] == 0:
                data.loc[i,"pattern"] = "Doji"
                # Calculate target and stoploss for the pattern
                if data.loc[i-1, 'Close'] > data.loc[i-1, 'Open']:
                    data.loc[i, 'Signal'] = 'Sell'
                    entry_price = data.loc[i, 'Open']
                    target_price = entry_price - data.loc[i, 'lower_shadow']
                    stoploss_price = entry_price + data.loc[i, 'upper_shadow']
                else:
                    data.loc[i, 'Signal'] = 'Buy'
                    entry_price = data.loc[i, 'Open']
                    target_price = entry_price + data.loc[i, 'upper_shadow']
                    stoploss_price = entry_price - data.loc[i, 'lower_shadow']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price

            # Piercing Pattern
            elif data.loc[i-1, 'Close'] < data.loc[i-1, 'Open'] and data.loc[i, 'Close'] > ((data.loc[i-1, 'Close'] + data.loc[i-1, 'Open']) / 2) and data.loc[i, 'Open'] < data.loc[i-1, 'Close']:
                data.loc[i,"pattern"] = "Piercing Pattern"
                # Calculate target, stoploss, and signal for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price + (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'Low']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Buy'

            # Dark Cloud Cover
            elif data.loc[i-1, 'Close'] > data.loc[i-1, 'Open'] and data.loc[i, 'Open'] > ((data.loc[i-1, 'Close'] + data.loc[i-1, 'Open']) / 2) and data.loc[i, 'Close'] < data.loc[i-1, 'Open']:
                data.loc[i,"pattern"] = "Dark Cloud Cover"
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price - (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'High']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Sell'
        
            # Bullish Harami
            elif (data.loc[i-1, 'Close'] > data.loc[i-1, 'Open']) and (data.loc[i, 'Open'] > data.loc[i-1, 'Close']) and (data.loc[i, 'Close'] < data.loc[i-1, 'Open']) and (data.loc[i, 'Close'] > data.loc[i, 'Open']):
                data.loc[i, 'pattern'] = 'Bullish Harami'
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price + (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'Low']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Buy'
        
      
            # Bearish Harami
            elif (data.loc[i-1, 'Close'] < data.loc[i-1, 'Open']) and (data.loc[i, 'Open'] < data.loc[i-1, 'Close']) and (data.loc[i, 'Close'] > data.loc[i-1, 'Open']) and (data.loc[i, 'Close'] < data.loc[i, 'Open']):
                data.loc[i, 'pattern'] = 'Bearish Harami'
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price - (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'High']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Sell'
    
            # Morning Star
            elif i >= 2 and data.loc[i-2, 'Close'] > data.loc[i-2, 'Open'] and abs(data.loc[i-1, 'Close'] - data.loc[i-1, 'Open']) < abs(data.loc[i-2, 'Close'] - data.loc[i-2, 'Open']) and data.loc[i, 'Close'] > data.loc[i-1, 'Close'] and data.loc[i, 'Open'] > data.loc[i-1, 'Close'] and data.loc[i, 'Close'] < data.loc[i-1, 'Open']:
                data.loc[i, 'pattern'] = 'Morning Star'
                # Calculate target and stoploss for the pattern
                entry_price = data.loc[i, 'Close']
                target_price = entry_price + (2 * data.loc[i, 'body'])
                stoploss_price = data.loc[i-1, 'Low']
                data.loc[i, 'Target'] = target_price
                data.loc[i, 'Entry'] = entry_price
                data.loc[i, 'Stoploss'] = stoploss_price
                data.loc[i, 'Signal'] = 'Buy'

            # Evening Star
            elif i >= 2 and data.loc[i-2, 'Close'] < data.loc[i-2, 'Open'] and abs(data.loc[i-1, 'Close'] - data.loc[i-1, 'Open']) < abs(data.loc[i-2, 'Close'] - data.loc[i-2, 'Open']) and data.loc[i, 'Close'] < data.loc[i-1, 'Open'] and data.loc[i, 'Open'] < data.loc[i-1, 'Open'] and data.loc[i, 'Close'] > data.loc[i-1, 'Close']:
                data.loc[i, 'pattern'] = 'Evening Star'
                data.loc[i, 'Target'] = data.loc[i, 'Close'] - (data.loc[i, 'High'] - data.loc[i, 'Low'])
                data.loc[i, 'Entry'] = data.loc[i, 'Close']
                data.loc[i, 'Stoploss'] = data.loc[i, 'High']
                data.loc[i, 'Signal'] = 'Sell'

        starttime = int(datetime.strptime("2019-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
        endtime = int(datetime.strptime("2023-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())

        mny_selected_stock = selected_stock.replace('.NS', '');

        money_control_url = f"https://priceapi.moneycontrol.com/techCharts/techChartController/history?symbol={mny_selected_stock}&resolution=5&from={starttime}&to={endtime}"

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        response = requests.get(money_control_url, headers=headers)
        response_data = response.json()

        stock_timestamp = response_data['t']
        Close = response_data['c']
        High = response_data['h']
        Low = response_data['l']
        Open = response_data['o']
        Volume = response_data['v']

        final_data = pd.DataFrame({'V1': pd.to_datetime(stock_timestamp, unit='s'),
                           'Close': Close,
                           'High': High,
                           'Low': Low,
                           'Open': Open,
                           'Volume': Volume})

        final_data.columns = ["Datetime", "Close", "High", "Low", "Open", "Volume"]


        # add 5:30 time to Datetime column
        final_data['Datetime'] = final_data['Datetime'] + pd.to_timedelta('5:30:00')

        final_data['Close'] = final_data['Close'].astype(float).astype(int)
        final_data['High'] = final_data['High'].astype(float).astype(int)
        final_data['Low'] = final_data['Low'].astype(float).astype(int)
        final_data['Open'] = final_data['Open'].astype(float).astype(int)
        final_data['Volume'] = final_data['Volume'].astype(float).astype(int)

        filtered_patterns = data[data['pattern'] != '']

        filtered_patterns.reset_index(inplace=True,drop=True)

        # function to check if target or stoploss has been hit
        def check_signal_hit(row):
            # find the corresponding 5-minute interval in final_data
            signal_datetime = pd.to_datetime(row['Date']) + pd.DateOffset(days=1)
            interval_start = signal_datetime.replace(hour=9, minute=15)
        #     print(interval_start)
        #     interval_end = signal_datetime.replace(hour=15, minute=30)
        #     mask = (final_data['Datetime'] >= interval_start) & (final_data['Datetime'] <= interval_end)
            mask = (final_data['Datetime'] >= interval_start)
            interval_data = final_data.loc[mask]
        #     print(interval_data)
            # check if the target or stoploss was hit
            if row['Signal'] == 'Buy':
                hit_target = interval_data['High'].max() >= row['Target']
                hit_stoploss = interval_data['Low'].min() <= row['Stoploss']
                if hit_target:
                    hit_timestamp = interval_data.loc[interval_data['High'] >= row['Target'], 'Datetime'].min()
                    hit_price = int(interval_data.loc[interval_data['Datetime'] == hit_timestamp,'High'])
                    return pd.Series({'Hit Timestamp': hit_timestamp, 'Hit Price': hit_price})
                elif hit_stoploss:
                    hit_timestamp = interval_data.loc[interval_data['Low'] <= row['Stoploss'], 'Datetime'].min()
                    hit_price = int(interval_data.loc[interval_data['Datetime'] == hit_timestamp,'Low'])
                    return pd.Series({'Hit Timestamp': hit_timestamp, 'Hit Price': hit_price})
                else:
                    return pd.Series({'Hit Timestamp': pd.NaT, 'Hit Price': pd.NaT})
            else:
                hit_target = interval_data['Low'].min() <= row['Target']
                hit_stoploss = interval_data['High'].max() >= row['Stoploss']
                if hit_target:
                    hit_timestamp = interval_data.loc[interval_data['Low'] <= row['Target'], 'Datetime'].min()
                    hit_price = int(interval_data.loc[interval_data['Datetime'] == hit_timestamp,'Low'])
                    return pd.Series({'Hit Timestamp': hit_timestamp, 'Hit Price': hit_price})
                elif hit_stoploss:
                    hit_timestamp = interval_data.loc[interval_data['High'] >= row['Stoploss'], 'Datetime'].min()
                    hit_price = int(interval_data.loc[interval_data['Datetime'] == hit_timestamp,'High'])
                    return pd.Series({'Hit Timestamp': hit_timestamp, 'Hit Price': hit_price})
                else:
                    return pd.Series({'Hit Timestamp': pd.NaT, 'Hit Price': pd.NaT})
            

        # apply the check_signal_hit function to each row of data
        filtered_patterns[['Hit Timestamp', 'Hit Price']] = filtered_patterns.apply(check_signal_hit, axis=1)

        # calculate profit or loss
        filtered_patterns['Profit/Loss'] = np.nan

        # iterate over the rows of filtered_patterns
        for i, row in filtered_patterns.iterrows():
            # check if the target or stoploss was hit
            if pd.notnull(row['Hit Timestamp']):
                if row['Signal'] == 'Buy':
                    pl = row['Hit Price'] - row['Entry']
                else:
                    pl = row['Entry'] - row['Hit Price']
                filtered_patterns.at[i, 'Profit/Loss'] = pl

        # create candlestick chart
        candlestick = go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])

        # add pattern text to chart
        annotations = []
        for i in range(len(filtered_patterns)):
            if filtered_patterns.loc[i, 'pattern'] != '':
                annotations.append(dict(x=filtered_patterns.loc[i, 'Date'], y=filtered_patterns.loc[i, 'Low'] - (filtered_patterns.loc[i, 'Low']*0.13), xref='x', yref='y', text=filtered_patterns.loc[i, 'pattern'], showarrow=True, font=dict(size=10, color='black'), align='center', textangle=-90))

        # create scatter plot with text
        scatter = go.Scatter(
            x=filtered_patterns['Date'],
            y=filtered_patterns['Close'],
            text=("Target: " + filtered_patterns['Target'].astype(str) + "<br>"
              "Entry: " + filtered_patterns['Entry'].astype(str) + "<br>"
              "Stoploss: " + filtered_patterns['Stoploss'].astype(str) + "<br>"
              "Signal: " + filtered_patterns['Signal'].astype(str) + "<br>"
              "Pattern: " + filtered_patterns['pattern'].astype(str) + "<br>"
              "Hit Timestamp: " + filtered_patterns['Hit Timestamp'].astype(str) + "<br>"
              "Hit Price: " + filtered_patterns['Hit Price'].astype(str) + "<br>"
              "Profit/Loss: " + filtered_patterns['Profit/Loss'].astype(str)),
            hoverinfo='text'
        )

        # combine scatter and candlestick chart
        chart_data = [candlestick, scatter]

        layout = {
            "title": "Stock Price Chart",
            "xaxis": {
                "rangebreaks": [{"bounds": ["sat", "mon"]}],
                "rangeslider": {"visible": False}
            },
            'yaxis': {'fixedrange': False}
        }

        fig = go.Figure(data=chart_data, layout=layout)

        fig.update_layout(annotations=annotations)

        # Convert the figure to HTML and return as a JSON object
        html_fig = pio.to_html(fig, full_html=False)

        # Return the HTML plot as a JSON object
        return jsonify(chart=html_fig,tabName=tabName)

    elif tabName == "#news_data":
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        money_control_new_url = "https://www.moneycontrol.com/india/stockpricequote/refineries/relianceindustries/RI"


        market_financials = requests.get(money_control_new_url, headers=headers).text

        soup = BeautifulSoup(market_financials, 'html.parser')

        data = soup.select_one('#news')

        # Extract all the data from anchor tags
        anchors = data.find_all('a')

        # Create an empty list to store the data
        final_data = []

        # Loop through each anchor tag and extract the link and title
        for a in anchors:
            link = a.get('href')
            title = a.get('title')
            if title:
                print(title)
            else:
                img = a.find('img')
                if img:
                    title = img.get('alt')
                else:
                    print('No title or alt text found.')
            if link and title:
                # Append the link and title to the data list
                final_data.append([link, title])

        money_control_news_data = pd.DataFrame(final_data,columns = ['Link','Headline'])

        # apply functions to headline column
        # money_control_news_data['entities'] = money_control_news_data['Headline'].apply(lambda x: extract_entities(x))
        # money_control_news_data['spacy_sentiment'], money_control_news_data['spacy_polarity'], money_control_news_data['spacy_pos_words'], money_control_news_data['spacy_neg_words'] = zip(*money_control_news_data['Headline'].apply(lambda x: get_sentiment(x, nlp=spacy.load("en_core_web_sm"))))
        # money_control_news_data['nltk_sentiment'], money_control_news_data['nltk_neg'], money_control_news_data['nltk_neu'], money_control_news_data['nltk_pos'], money_control_news_data['nltk_compound'] = zip(*money_control_news_data['Headline'].apply(lambda x: get_nltk_sentiment(x)))
        # # money_control_news_data['amazon_sentiment_scores'] = money_control_news_data['Headline'].apply(lambda x: get_amazon_sentiment_scores(x))
        # # print(df)
        # money_control_news_data['finbert_sentiment'] = get_finbert_sentiments(money_control_news_data['Headline'].tolist())


        # nlp = spacy.load("en_core_web_sm")

        # text = "This is a positive sentence"
        # spacy_sentiment, sentiment, spacy_positive_words, spacy_negative_words = get_sentiment(text, nlp)

        # print(spacy_sentiment)
        # print(sentiment)
        # print(spacy_positive_words)
        # print(spacy_negative_words)

        # text = "This is a positive sentence"
        # sentiment = get_nltk_sentiment(text)
        # # Convert the list of sentiment scores to a dictionary
        # sentiment_dict = {'sentiment': sentiment[0], 'neutral': sentiment[1], 'positive': sentiment[2], 'compound': sentiment[3]}

        # print(sentiment_dict)

        # sentiment_scores = get_amazon_sentiment_scores(text)

        # print(sentiment_scores)

        # sentiment = get_finbert_sentiments(text)
        # print(sentiment)

        

        economic_times_url = "https://economictimes.indiatimes.com/reliance-industries-ltd/stocks/companyid-13215.cms"
        market_financials = requests.get(economic_times_url, headers=headers).text
        soup = BeautifulSoup(market_financials, 'html.parser')
        stories = soup.find_all('div', {'class': 'news_sec'})

        final_data = []

        for item in stories:
            links = item.find_all('a')
            for link in links:
                href = link['href']
                title = link.text.strip()
                if '.cms' in href:
                    print(title)
                    final_data.append(["https://economictimes.indiatimes.com"+str(href), title])

        economic_times_news_data = pd.DataFrame(final_data,columns = ['Link','Headline'])


        final_data = []
        live_mint_new_url = "https://www.livemint.com/market/market-stats/stocks-reliance-industries-share-price-nse-bse-s0003018"
        market_financials = requests.get(live_mint_new_url, headers=headers).text
        soup = BeautifulSoup(market_financials, 'html.parser')
        soup = soup.select_one('#stock_news')
        stories = soup.find_all('div', {'class': 'headlineSec'})
        for story in stories:
            link = story.find('h2', {'class': 'headline'})
        #     print(link)
            if link is not None:
                link = story.find('a')
                href = link['href']
                title = link.text.strip()
                final_data.append(["https://www.livemint.com"+str(href), title])
                print('Href:', href)
                print('Title:', title)
        live_mint_news_data = pd.DataFrame(final_data,columns = ['Link','Headline'])

        news_data = {"money_control_news": money_control_news_data.to_dict(),
                    "economic_times_news_data":economic_times_news_data.to_dict(),
                       "live_mint_news_data":live_mint_news_data.to_dict()}

        return jsonify(news_data=news_data,tabName=tabName)
    else:
        return jsonify(tabName=tabName)

@app.route('/orders_preview')
def orders_preview():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('client_data_update.html', current_date=current_date)

@app.route("/get_data", methods=["POST"])
def get_data():
    client_id = request.get_json()["selectedClient"]
    date_selected = request.get_json()["selectedDate"]

    print(client_id)
    print(date_selected)

    if date_selected == "":
    	date_selected = '2023-01-19'
    print(date_selected)
    if client_id != "All":
    	final_position_data,final_open_data,final_stoploss_data,final_completed_orders,final_closed_positions = get_display_data(client_id,date_selected,db)
    	# data = get_display_data(client_id,date_selected)

    data = {"final_position_data": final_position_data.to_dict(),
    		 "final_open_data": final_open_data.to_dict(),
    		 "final_stoploss_data": final_stoploss_data.to_dict(),
    		 "final_completed_orders": final_completed_orders.to_dict(),
    		 "final_closed_positions": final_closed_positions.to_dict(),
    		 }

    print(data)
    return jsonify(data)

@app.route('/technical_preview')
def technical_preview():
    return render_template('technical_preview.html')

@app.route('/get_technical_data', methods=['POST'])
def get_technical_data():
    selected_value = request.get_json()["selected_value"]
    interval_value = request.get_json()["interval_value"]

    print(selected_value)
    print(interval_value)

    technical_indicators = pd.DataFrame()

    # final_orders_raw_data = collection.find({"execution_date":str(date_selected)})

    # final_orders_raw_data =  pd.DataFrame(list(final_orders_raw_data))



    if interval_value == "1min":
    	if selected_value == "All":
    		technical = db.technical_indicator_1_minutes.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_1_minutes.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    elif interval_value == "5min":
    	if selected_value == "All":
    		technical = db.technical_indicator_5_minutes.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_5_minutes.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    elif interval_value == "15min":
    	if selected_value == "All":
    		technical = db.technical_indicator_15_minutes.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_15_minutes.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))

    elif interval_value == "30min":
    	if selected_value == "All":
    		technical = db.technical_indicator_30_minutes.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_30_minutes.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))

    elif interval_value == "60min":
    	if selected_value == "All":
    		technical = db.technical_indicator_60_minutes.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_60_minutes.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))


    elif interval_value == "1day":
    	if selected_value == "All":
    		technical = db.technical_indicator_1_day.find().sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))
    	else:
    		technical = db.technical_indicator_1_day.find({"Stock":str(selected_value)}).sort("Datetime", -1)
    		technical_indicators =  pd.DataFrame(list(technical))

    if len(technical_indicators)>0:
    	technical_indicators = technical_indicators[['Stock', 'Datetime', 'Open', 'High', 'Low','Close', 'Volume','buy_probability', 'sell_probability', 'SMA_Call', 'RSI_Call','MACD_Call', 'Pivot_Call', 'PCR_Call', 'BB_Call','VWAP_Call','SuperTrend_Call']]
    	technical_indicators['buy_probability'] = technical_indicators['buy_probability'].fillna(0)
    	technical_indicators['sell_probability'] = technical_indicators['sell_probability'].fillna(0)

    else:
    	technical_indicators = pd.DataFrame(columns=['Stock', 'Datetime', 'Open', 'High', 'Low','Close', 'Volume','buy_probability', 'sell_probability', 'SMA_Call', 'RSI_Call','MACD_Call', 'Pivot_Call', 'PCR_Call', 'BB_Call','VWAP_Call','SuperTrend_Call'])

    print(technical_indicators)
    technical_indicators = technical_indicators.fillna('-')


    fig = go.Figure()

    if len(technical_indicators) > 0:
        # Add buy_probability trace
        fig.add_trace(go.Scatter(x=technical_indicators['Datetime'], y=technical_indicators['buy_probability'], name='Buy Probability', yaxis='y1'))

        # Add sell_probability trace
        fig.add_trace(go.Scatter(x=technical_indicators['Datetime'], y=technical_indicators['sell_probability'], name='Sell Probability', yaxis='y2'))

        # Customize the layout
        fig.update_layout(
            title='Buy Probability vs Sell Probability',
            xaxis=dict(title='Date Time'),
            yaxis=dict(title='Buy Probability', side='left'),
            yaxis2=dict(title='Sell Probability', side='right', overlaying='y', showgrid=False)
        )


    # Convert the chart to JSON format
    chart_json = fig.to_json()

    paper_data = {"technical_indicators": technical_indicators.to_dict(),
                    "chart":json.loads(chart_json)}

    return jsonify(paper_data=paper_data)

@app.route("/options_signals",methods=["GET","POST"])
def options_signals_preview():
	options_signals = []

	if request.method == "POST":
		selected_value = request.form.get("dropdown")
		print(selected_value)
		# for signal in db.options_signals.find({"Stock":str(selected_value)}).sort("Datetime", 1):
		for signal in db.futures_options_signals.find({"Stock":str(selected_value)}).sort("Datetime", 1):
			
			signal["_id"] = str(signal["_id"])
			# order["Strategy"] = str(order["Strategy"])
			# order["Stock"] = str(order["Stock"])
			# order["Signal"] = str(order["Signal"])
			# # order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
			# order["Datetime"] = str(order["Datetime"])
			# order["buy_probability"] = str(order["buy_probability"])
			# order["sell_probability"] = str(order["sell_probability"])
			
			options_signals.append(signal)

	else:
		# for signal in db.options_signals.find().sort("Datetime", 1):
		for signal in db.futures_options_signals.find().sort("Datetime", 1):
			signal["_id"] = str(signal["_id"])
			# order["Strategy"] = str(order["Strategy"])
			# order["Stock"] = str(order["Stock"])
			# order["Signal"] = str(order["Signal"])
			# # order["Datetime"] = order["Datetime"].strftime('%d %m %Y %H:%M:%S')
			# order["Datetime"] = str(order["Datetime"])
			# order["buy_probability"] = str(order["buy_probability"])
			# order["sell_probability"] = str(order["sell_probability"])
			
			options_signals.append(signal)

	# print(daily_orders)
	print(options_signals[0])

	# options_signals = 

	# options_signals.sort_values(by='Datetime', ascending=True, inplace=True)

	return render_template('options_signals.html', value=options_signals)

@app.route('/algo_trade')
def algo_trade():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('completed_orders.html', current_date=current_date)

@app.route('/support_and_resistance')
def support_and_resistance():
	return render_template('support_and_resistance.html')

@app.route('/ai_trading')
def ai_trading():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('ai_trading_latest.html', current_date=current_date)

@app.route('/get_ai_trading', methods=['POST'])
def get_ai_trading():
    selectedOption = request.get_json()["selectedOption"]
    selectedDate = request.get_json()["selectedDate"]
    selectedLine = request.get_json()["selectedLine"]
    print(selectedLine)
    

    figure,bar_chart_data, pie_chart_data, output_data = get_combined_chart(selectedOption,selectedDate,selectedLine,db)

	# debugger;

    # print(figure)

    # fig = Figure({
    # 'data': [{'close': array([41651.  , 41678.25, 41680.    ]),
    #           'high': array([41777.9 , 41729.2 , 41715.75 ]),
    #           'low': array([41544.75, 41612.7 , 41570.  ]),
    #           'open': array([41660.05, 41651.6 , 41677.85]),
    #           'type': 'candlestick',
    #           'x': array([datetime.datetime(2023, 2, 6, 9, 15),
    #                       datetime.datetime(2023, 2, 6, 9, 20),
    #                       datetime.datetime(2023, 2, 6, 9, 25)], dtype=object)},
    #          {'mode': 'lines',
    #           'name': 'Arima Pivot Point',
    #           'type': 'scatter',
    #           'x': array([datetime.datetime(2023, 2, 6, 9, 15),
    #                       datetime.datetime(2023, 2, 6, 9, 20),
    #                       datetime.datetime(2023, 2, 6, 9, 25)], dtype=object),
    #           'y': array([41499.7 , 41499.7 , 41499.7 ])}],
    # 'layout': {'template': '...',
    #            'title': {'text': 'Orders Chart'},
    #            'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}],
    #                      'rangeslider': {'visible': False},
    #                      'type': 'category'}}
    # })


    # fig_dict = figure.to_dict()

    # # Serialize the dictionary to JSON
    # fig_json = json.dumps(fig_dict)

    # print(fig_json)

    # return jsonify(figure=figure.to_html(),figure=figure.to_html())


    # return jsonify({
    #     'candlestick_chart': figure.to_html(full_html=False, include_plotlyjs=False),
    #     'bar_chart': bar_chart_data.to_html(full_html=False, include_plotlyjs=False),
    #     'pie_chart': pie_chart_data.to_html(full_html=False, include_plotlyjs=False),
    #     'output_data': output_data.to_html(classes=['table', 'table-striped'])
    # })

    return jsonify({
        'candlestick_chart': figure.to_html(full_html=False, include_plotlyjs=False),
        'bar_chart': json.dumps(bar_chart_data, cls=plotly.utils.PlotlyJSONEncoder),
        'pie_chart': json.dumps(pie_chart_data, cls=plotly.utils.PlotlyJSONEncoder),
        'output_data': output_data.to_html(classes=['table', 'table-striped'])
    })

@app.route("/open_interest",methods=["GET"])
def open_interest():
    ts = str(datetime.now(timezone("Asia/Kolkata")))

    baseurl = "https://www.nseindia.com/"
    # new_url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    # response = session.get(new_url, headers=headers, timeout=5, cookies=cookies)
    # print(response.json())

    new_url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'


    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(new_url,headers=headers,timeout=10,cookies=cookies)
    # print(page.text)
    dajs = json.loads(page.text)

    ce_values = [data['CE'] for data in dajs['records']['data'] if "CE" in data]

    pe_values = [data['PE'] for data in dajs['records']['data'] if "PE" in data]

    ce_dt = pd.DataFrame(ce_values).sort_values(['strikePrice'])
    pe_dt = pd.DataFrame(pe_values).sort_values(['strikePrice'])

    ce = ce_dt[['askPrice', 'strikePrice','bidprice', 'bidQty', 'change', 'changeinOpenInterest', 'expiryDate', 
       'identifier', 'impliedVolatility', 'lastPrice',  'openInterest', 'pChange', 'pchangeinOpenInterest',
        'totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'underlying', 'underlyingValue']]

    ce = ce.set_axis(['askprice', 'strikeprice','bidprice', 'bidqty', 'change', 'changeinopeninterest', 'expirydate', 
       'identifier', 'impliedvolatility', 'lastprice',  'openinterest', 'pchange', 'pchangeinopeninterest',
       'totalbuyquantity', 'totalsellquantity', 'totaltradedvolume', 'underlying', 'underlyingvalue'], axis=1, inplace=False)

    ce['type'] = "CALL"
    ce['time'] = ts


    ce.columns = ['call_askprice', 'call_strikeprice','call_bidprice', 'call_bidqty', 'call_change', 'call_changeinopeninterest', 'call_expirydate', 
                'call_identifier', 'call_impliedvolatility', 'call_lastprice',  'call_openinterest', 'call_pchange', 'call_pchangeinopeninterest',
                'call_totalbuyquantity', 'call_totalsellquantity', 'call_totaltradedvolume', 'call_underlying', 'call_underlyingvalue','call_type','call_time']


    pe = pe_dt[['askPrice', 'strikePrice','bidprice', 'bidQty', 'change', 'changeinOpenInterest', 'expiryDate', 
       'identifier', 'impliedVolatility', 'lastPrice',  'openInterest', 'pChange', 'pchangeinOpenInterest',
        'totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'underlying', 'underlyingValue']]

    pe = pe.set_axis(['askprice', 'strikeprice','bidprice', 'bidqty', 'change', 'changeinopeninterest', 'expirydate', 
       'identifier', 'impliedvolatility', 'lastprice',  'openinterest', 'pchange', 'pchangeinopeninterest',
        'totalbuyquantity', 'totalsellquantity', 'totaltradedvolume', 'underlying', 'underlyingvalue'], axis=1, inplace=False)
    pe['type'] = "PUT"
    pe['time'] = ts

    pe.columns = ['put_askprice', 'put_strikeprice','put_bidprice', 'put_bidqty', 'put_change', 'put_changeinopeninterest', 'put_expirydate', 
       'put_identifier', 'put_impliedvolatility', 'put_lastprice',  'put_openinterest', 'put_pchange', 'put_pchangeinopeninterest',
        'put_totalbuyquantity', 'put_totalsellquantity', 'put_totaltradedvolume', 'put_underlying', 'put_underlyingvalue','put_type','put_time']

    print("Current expiry = 16-Feb-2023 and needs to be changed")

    today_now = datetime.now(timezone("Asia/Kolkata")) 

    expiry_date = today_now

    if today_now.strftime("%w") == "1":
        expiry_date = today_now + timedelta(days=3)
    elif today_now.strftime("%w") == "2":
        expiry_date = today_now + timedelta(days=9)
    elif today_now.strftime("%w") == "3":
        expiry_date = today_now + timedelta(days=8)
    elif today_now.strftime("%w") == "4":
        expiry_date = today_now + timedelta(days=7)
    elif today_now.strftime("%w") == "5":
        expiry_date = today_now + timedelta(days=6)
    elif today_now.strftime("%w") == "6":
        expiry_date = today_now + timedelta(days=5)
    elif today_now.strftime("%w") == "7":
        expiry_date = today_now + timedelta(days=4)

    print("Expiry date")
    print(expiry_date)

    latest_ce = ce.loc[ce['call_expirydate'] == expiry_date.strftime("%d-%b-%Y"),]
    latest_pe = pe.loc[pe['put_expirydate'] == expiry_date.strftime("%d-%b-%Y"),]
    
    # latest_pe = pe.loc[pe['put_expirydate'] == '16-Feb-2023',]

    merged_data = pd.merge(latest_ce, latest_pe,left_on = ['call_strikeprice','call_expirydate'],right_on = ['put_strikeprice','put_expirydate'] , how='left')

    merged_data = merged_data.fillna(0)

    merged_data = merged_data.astype({'call_strikeprice':'int64', 
                                   'call_bidqty':'int64',
                                   'call_changeinopeninterest':'int64',
                                   'call_totalbuyquantity':'int64',
                                   'call_totalsellquantity':'int64',
                                   'call_totaltradedvolume':'int64',
                                   'call_underlyingvalue':'int64',
                                   'put_strikeprice':'int64', 
                                   'put_bidqty':'int64',
                                   'put_changeinopeninterest':'int64',
                                   'put_totalbuyquantity':'int64',
                                   'put_totalsellquantity':'int64',
                                   'put_totaltradedvolume':'int64',
                                   'put_underlyingvalue':'int64',
                                   
                                   'call_askprice':'float64',
                                   'call_bidprice':'float64',
                                   'call_change':'float64',
                                   'call_impliedvolatility':'float64',
                                   'call_lastprice':'float64',
                                   'call_openinterest':'float64',
                                   'call_pchange':'float64',
                                   'call_changeinopeninterest':'float64',
                                   
                                   'put_askprice':'float64',
                                   'put_bidprice':'float64',
                                   'put_change':'float64',
                                   'put_impliedvolatility':'float64',
                                   'put_lastprice':'float64',
                                   'put_openinterest':'float64',
                                   'put_pchange':'float64',
                                   'put_changeinopeninterest':'float64' 
                                  })




    collection = db["Stocks_data_5_minutes"]
    live_data = collection.find({"instrumenttype": "OPTIDX", "Stock": "Nifty"})
    live_data = pd.DataFrame(list(live_data))

    live_data["Datetime"] = live_data["Datetime"] + timedelta(hours=5, minutes=30)

    latest_data = live_data.tail(1)

    latest_data.reset_index(level=0, inplace=True, drop=True)

    current_close = latest_data.loc[0, "Close"]

    current_strike = current_close + (50 - current_close % 50) if current_close% 50 > 25 else (current_close - current_close % 50)

    current_strike = current_strike.astype(int)
    b = list(range(current_strike-500, current_strike+500, 50))

    merged_filter_data = merged_data.loc[(merged_data['call_strikeprice'] >= current_strike-500) & (merged_data['call_strikeprice'] < current_strike+500) ,]


    merged_filter_data.reset_index(drop=True,inplace=True)

    plot_df = pd.DataFrame(list(zip(b,merged_filter_data['call_openinterest'],merged_filter_data['put_openinterest']))
                      ,columns=["Strike","Call OI","Put OI"])

    print(plot_df)

    fig = go.Figure(data=[go.Bar(
        name = 'Call OI',
        x = plot_df['Strike'],
        y = plot_df['Call OI']
       ),
                           go.Bar(
        name = 'Put OI',
        x = plot_df['Strike'],
        y = plot_df['Put OI']
       )
    ])

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="OI for Nifty"
    return render_template('open_interest.html', graphJSON=graphJSON)

def total_loss_at_strike(chain, expiry_price):
    """Calculate loss at strike price"""
    # All call options with strike price below the expiry price will result in loss for option writers
    in_money_calls = chain[chain['call_strikeprice'] < expiry_price][["call_openinterest", "call_strikeprice"]]
    in_money_calls["call_loss"] = (expiry_price - in_money_calls['call_strikeprice'])*in_money_calls["call_openinterest"]

    # All put options with strike price above the expiry price will result in loss for option writers
    in_money_puts = chain[chain['put_strikeprice'] > expiry_price][["put_openinterest", "put_strikeprice"]]
    in_money_puts["put_loss"] = (in_money_puts['put_strikeprice'] - expiry_price)*in_money_puts["put_openinterest"]
    total_loss = in_money_calls["call_loss"].sum() + in_money_puts["put_loss"].sum()

    return total_loss

@app.route("/max_pain",methods=["GET"])
def max_pain():
    ts = str(datetime.now(timezone("Asia/Kolkata")))

    baseurl = "https://www.nseindia.com/"
    # new_url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    # response = session.get(new_url, headers=headers, timeout=5, cookies=cookies)
    # print(response.json())

    new_url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'


    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(new_url,headers=headers,timeout=10,cookies=cookies)
    # print(page.text)
    dajs = json.loads(page.text)

    ce_values = [data['CE'] for data in dajs['records']['data'] if "CE" in data]

    pe_values = [data['PE'] for data in dajs['records']['data'] if "PE" in data]

    ce_dt = pd.DataFrame(ce_values).sort_values(['strikePrice'])
    pe_dt = pd.DataFrame(pe_values).sort_values(['strikePrice'])

    ce = ce_dt[['askPrice', 'strikePrice','bidprice', 'bidQty', 'change', 'changeinOpenInterest', 'expiryDate', 
       'identifier', 'impliedVolatility', 'lastPrice',  'openInterest', 'pChange', 'pchangeinOpenInterest',
        'totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'underlying', 'underlyingValue']]

    ce = ce.set_axis(['askprice', 'strikeprice','bidprice', 'bidqty', 'change', 'changeinopeninterest', 'expirydate', 
       'identifier', 'impliedvolatility', 'lastprice',  'openinterest', 'pchange', 'pchangeinopeninterest',
       'totalbuyquantity', 'totalsellquantity', 'totaltradedvolume', 'underlying', 'underlyingvalue'], axis=1, inplace=False)

    ce['type'] = "CALL"
    ce['time'] = ts


    ce.columns = ['call_askprice', 'call_strikeprice','call_bidprice', 'call_bidqty', 'call_change', 'call_changeinopeninterest', 'call_expirydate', 
                'call_identifier', 'call_impliedvolatility', 'call_lastprice',  'call_openinterest', 'call_pchange', 'call_pchangeinopeninterest',
                'call_totalbuyquantity', 'call_totalsellquantity', 'call_totaltradedvolume', 'call_underlying', 'call_underlyingvalue','call_type','call_time']


    pe = pe_dt[['askPrice', 'strikePrice','bidprice', 'bidQty', 'change', 'changeinOpenInterest', 'expiryDate', 
       'identifier', 'impliedVolatility', 'lastPrice',  'openInterest', 'pChange', 'pchangeinOpenInterest',
        'totalBuyQuantity', 'totalSellQuantity', 'totalTradedVolume', 'underlying', 'underlyingValue']]

    pe = pe.set_axis(['askprice', 'strikeprice','bidprice', 'bidqty', 'change', 'changeinopeninterest', 'expirydate', 
       'identifier', 'impliedvolatility', 'lastprice',  'openinterest', 'pchange', 'pchangeinopeninterest',
        'totalbuyquantity', 'totalsellquantity', 'totaltradedvolume', 'underlying', 'underlyingvalue'], axis=1, inplace=False)
    pe['type'] = "PUT"
    pe['time'] = ts

    pe.columns = ['put_askprice', 'put_strikeprice','put_bidprice', 'put_bidqty', 'put_change', 'put_changeinopeninterest', 'put_expirydate', 
       'put_identifier', 'put_impliedvolatility', 'put_lastprice',  'put_openinterest', 'put_pchange', 'put_pchangeinopeninterest',
        'put_totalbuyquantity', 'put_totalsellquantity', 'put_totaltradedvolume', 'put_underlying', 'put_underlyingvalue','put_type','put_time']

    print("Current expiry = 2023-19-01 and needs to be changed")

    today_now = datetime.now(timezone("Asia/Kolkata")) 

    expiry_date = today_now

    if today_now.strftime("%w") == "1":
        expiry_date = today_now + timedelta(days=3)
    elif today_now.strftime("%w") == "2":
        expiry_date = today_now + timedelta(days=9)
    elif today_now.strftime("%w") == "3":
        expiry_date = today_now + timedelta(days=8)
    elif today_now.strftime("%w") == "4":
        expiry_date = today_now + timedelta(days=7)
    elif today_now.strftime("%w") == "5":
        expiry_date = today_now + timedelta(days=6)
    elif today_now.strftime("%w") == "6":
        expiry_date = today_now + timedelta(days=5)
    elif today_now.strftime("%w") == "7":
        expiry_date = today_now + timedelta(days=4)

    print("Expiry date")
    print(expiry_date)

    latest_ce = ce.loc[ce['call_expirydate'] == expiry_date.strftime("%d-%b-%Y"),]
    latest_pe = pe.loc[pe['put_expirydate'] == expiry_date.strftime("%d-%b-%Y"),]

    # latest_ce = ce.loc[ce['call_expirydate'] == '16-Feb-2023',]
    # latest_pe = pe.loc[pe['put_expirydate'] == '16-Feb-2023',]

    merged_data = pd.merge(latest_ce, latest_pe,left_on = ['call_strikeprice','call_expirydate'],right_on = ['put_strikeprice','put_expirydate'] , how='left')

    merged_data = merged_data.fillna(0)

    merged_data = merged_data.astype({'call_strikeprice':'int64', 
                                   'call_bidqty':'int64',
                                   'call_changeinopeninterest':'int64',
                                   'call_totalbuyquantity':'int64',
                                   'call_totalsellquantity':'int64',
                                   'call_totaltradedvolume':'int64',
                                   'call_underlyingvalue':'int64',
                                   'put_strikeprice':'int64', 
                                   'put_bidqty':'int64',
                                   'put_changeinopeninterest':'int64',
                                   'put_totalbuyquantity':'int64',
                                   'put_totalsellquantity':'int64',
                                   'put_totaltradedvolume':'int64',
                                   'put_underlyingvalue':'int64',
                                   
                                   'call_askprice':'float64',
                                   'call_bidprice':'float64',
                                   'call_change':'float64',
                                   'call_impliedvolatility':'float64',
                                   'call_lastprice':'float64',
                                   'call_openinterest':'float64',
                                   'call_pchange':'float64',
                                   'call_changeinopeninterest':'float64',
                                   
                                   'put_askprice':'float64',
                                   'put_bidprice':'float64',
                                   'put_change':'float64',
                                   'put_impliedvolatility':'float64',
                                   'put_lastprice':'float64',
                                   'put_openinterest':'float64',
                                   'put_pchange':'float64',
                                   'put_changeinopeninterest':'float64' 
                                  })

    strikes = list(merged_data['call_strikeprice'])
    # Let us calculate loss for each strike price

    losses = [total_loss_at_strike(merged_data, strike)/1000000 for strike in strikes] 

    new_df = pd.DataFrame(list(zip(strikes,losses)),columns=["strikes","losses"])

    print(new_df)

    fig = px.line(new_df,x="strikes",y="losses")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    m = losses.index(min(losses))

    max_pain_point = strikes[m]

    print(max_pain_point)

    return render_template('max_pain.html', graphJSON=graphJSON,max_pain_point=max_pain_point)

@app.route("/fii_and_dii",methods=["GET"])
def fii_and_dii():
    # current_start_date = "2022-10-01"
    # current_end_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")

    current_start_date = request.args.get("start_date", "2022-10-01")
    current_end_date = request.args.get("end_date", datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d"))



    return render_template("fii_and_dii.html", start_date = current_start_date, end_date = current_end_date)


    

    # return render_template("fii_and_dii.html", index_plot=figure.to_html(),options_plot = figure2.to_html())


@app.route('/get-fii-dii-data', methods=['POST'])
def send_data():
    current_start_date = request.get_json()["current_start_date"]
    current_end_date = request.get_json()["current_end_date"]
    print(current_end_date)
    print(current_start_date)

    # Build the query to find documents with a 'ClientType' of 'FII' or 'DII'
    # and a 'Date' field between the start and end date
    query = {
        'ClientType': {'$in': ['FII', 'DII']},
        'Date': {'$gte': str(current_start_date), '$lt': str(current_end_date)}
    }

    print(query)

    # Execute the query and sort the results by the 'Date' field in ascending order
    cursor = db['fii_dii_data'].find(query)
    fii_dii_data = cursor.sort([('Date', 1)])

    # fii_dii_data = db["fii_dii_data"].find({'ClientType':{'$in':['FII','DII']},'Date':{$gte:ISODate("2022-12-01"),$lt:ISODate("2023-01-20")}}).sort([('Date', 1)])
    fii_dii_data =  pd.DataFrame(list(fii_dii_data))

    print(fii_dii_data.head())


    fii_data = fii_dii_data[fii_dii_data['ClientType'] == "FII"]
    dii_data = fii_dii_data[fii_dii_data['ClientType'] == "DII"]

    fii_data.reset_index(inplace=True,drop=True)
    dii_data.reset_index(inplace=True,drop=True)

    fii_data['FutureIndexLong'] = fii_data['FutureIndexLong'].astype(int)
    dii_data['FutureIndexLong'] = dii_data['FutureIndexLong'].astype(int)
    fii_data['FutureIndexShort'] = fii_data['FutureIndexShort'].astype(int)
    dii_data['FutureIndexShort'] = dii_data['FutureIndexShort'].astype(int)

    fii_data['OptionIndexCallLong'] = fii_data['OptionIndexCallLong'].astype(float).astype(int)
    fii_data['OptionIndexPutLong'] = fii_data['OptionIndexPutLong'].astype(float).astype(int)
    fii_data['OptionIndexCallShort'] = fii_data['OptionIndexCallShort'].astype(float).astype(int)
    fii_data['OptionIndexPutShort'] = fii_data['OptionIndexPutShort'].astype(float).astype(int)



    fii_FutureIndexLong = go.Scatter(x=fii_data['Date'], y=fii_data['FutureIndexLong'],
                        mode='lines+markers',
                        name='FII Future Index Long')
    dii_FutureIndexLong = go.Scatter(x=dii_data['Date'], y=dii_data['FutureIndexLong'],
                        mode='lines+markers',
                        name='DII Future Index Long')

    fii_FutureIndexShort = go.Scatter(x=fii_data['Date'], y=fii_data['FutureIndexShort'],
                        mode='lines+markers',
                        name='FII Future Index Long')
    dii_FutureIndexShort = go.Scatter(x=dii_data['Date'], y=dii_data['FutureIndexShort'],
                        mode='lines+markers',
                        name='DII Future Index Long')


    fii_OptionIndexCallLong = go.Scatter(x=fii_data['Date'], y=fii_data['OptionIndexCallLong'],
                        mode='lines+markers',
                        name='FII Option Index Call Long')
    fii_OptionIndexPutLong = go.Scatter(x=fii_data['Date'], y=fii_data['OptionIndexPutLong'],
                        mode='lines+markers',
                        name='FII Option Index Put Long')

    fii_OptionIndexCallShort = go.Scatter(x=fii_data['Date'], y=fii_data['OptionIndexCallShort'],
                        mode='lines+markers',
                        name='FII Option Index Call Short')
    fii_OptionIndexPutShort = go.Scatter(x=fii_data['Date'], y=fii_data['OptionIndexPutShort'],
                        mode='lines+markers',
                        name='FII Option Index Put Short')

    data = [fii_FutureIndexLong,dii_FutureIndexLong,fii_FutureIndexShort,dii_FutureIndexShort]
    data2 = [fii_OptionIndexCallLong,fii_OptionIndexPutLong,fii_OptionIndexCallShort,fii_OptionIndexPutShort]

    layout = {'title': 'FII And DII Futures '}
    layout2 = {'title': 'FII And DII Options Index '}

    figure = go.Figure(data=data, layout=layout)
    figure2 = go.Figure(data=data2, layout=layout2)

    # chart_html1 = pio.to_html(figure,full_html=True)
    # chart_html2 = pio.to_html(figure2,full_html=True)

    return jsonify(chartHtml1=figure.to_json(),chartHtml2=figure2.to_json())

@app.route("/sector_analysis",methods=["GET"])
def sector_analysis():

    current_start_date = request.args.get("start_date", "2023-01-01")
    current_end_date = request.args.get("end_date", datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d"))

    return render_template("sector_analysis.html", start_date = current_start_date, end_date = current_end_date)

@app.route('/get_sector_analysis', methods=['POST'])
def get_sector_analysis():
	start_date = request.get_json()["current_start_date"]
	end_date = request.get_json()["current_end_date"]

	start_date = datetime.strptime(start_date, '%Y-%m-%d')
	end_date = datetime.strptime(end_date, '%Y-%m-%d')

	print(start_date)

	symbols = {
	    'NIFTY IT': 'Nifty IT',
	    'NIFTY PHARMA': 'Nifty Pharma',
	    'NIFTY AUTO': 'Nifty Auto',
	    'NIFTY REALTY': 'Nifty Realty',
	    'NIFTY 50': 'Nifty 50',
	    'NIFTY BANK': 'Bank Nifty',
	    'NIFTY ENERGY': 'Nifty Energy',
	    'NIFTY FMCG': 'Nifty FMCG',
	    'NIFTY MEDIA': 'Nifty Media'
	}
	# Fetch the historical data
	data = {}
	for symbol, name in symbols.items():
	    data[name] = get_history(symbol=symbol, start=start_date, end=end_date, index=True)

	# Compute the daily percentage change for each stock
	percent_changes = {}
	for name, df in data.items():
	    percent_changes[name] = df['Close'].pct_change()*100


	# Convert percent_changes dictionary to a pandas DataFrame
	df = pd.DataFrame(percent_changes)

	df = df.dropna()

	# Convert index to pandas datetime index and format the dates
	df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

	# Create the heatmap using plotly.graph_objects
	fig = go.Figure(data=go.Heatmap(
	                   z=df.values,
	                   x=df.columns,
	                   y=df.index,
	                   colorscale='RdYlGn',
	                   zmin=-3,  # minimum value for the color scale
                   	   zmax=3,  # maximum value for the color scale
	                   colorbar=dict(title='% Change')
	                 ))

	# Update the layout of the heatmap
	fig.update_layout(
	    title='Daily % Change in Stock Prices',
	    xaxis_title='Stocks',
	    yaxis_title='Dates',
	    template='plotly_dark'
	)

	response_data = {
	    "sector_plot": fig.to_html()
	}

	return jsonify(response_data)

@app.route('/payoff_chart')
def payoff_chart():
     # Define option parameters
    strike_price = 100
    stock_price = np.linspace(80, 120, num=41)

    # Calculate option payoffs
    call_payoff = np.maximum(stock_price - strike_price, 0)
    put_payoff = np.maximum(strike_price - stock_price, 0)

    # Create payoff chart
    call_trace = go.Scatter(x=stock_price, y=call_payoff, mode='lines', name='Call Option')
    put_trace = go.Scatter(x=stock_price, y=put_payoff, mode='lines', name='Put Option')
    data = [call_trace, put_trace]
    layout = go.Layout(title='Option Payoff Chart', xaxis=dict(title='Stock Price'), yaxis=dict(title='Profit/Loss'))
    fig = go.Figure(data=data, layout=layout)

    plot = plotly.offline.plot(fig, output_type="div", include_plotlyjs=False)

    # Render template with chart
    return render_template('payoff_chart.html', plot=fig)


@app.route('/generate-pay-off', methods=['POST'])
def generate_pay_off():
    selectedIndex = request.get_json()["selectedIndex"]
    selectedStrike = request.get_json()["selectedStrike"]
    selectedDirection = request.get_json()["selectedDirection"]
    selectedOptionPrice = request.get_json()["selectedOptionPrice"]
    selectedLotsize = request.get_json()["selectedLotsize"]
    selectedStrategy = request.get_json()["selectedStrategy"]

    print(selectedIndex)
    print(selectedStrike)

    strike_price = [selectedStrike]
    stock_price = []
    Price = selectedOptionPrice
    lotsize = 50

    if selectedIndex == "Nifty":
    	stock_price = list(np.arange(17000, 19000, 3))
    	lotsize = 50
    else:
    	stock_price = list(np.arange(41000, 44000, 5))
    	lotsize = 25

    payoff = []

    for sp in strike_price:
    	if selectedStrategy == "long_call": 
    		payoff.append(long_call(stock_price, int(sp), int(Price)))
    	if selectedStrategy == "long_put": 
    		payoff.append(long_put(stock_price, int(sp), int(Price)))
    	if selectedStrategy == "short_call": 
    		payoff.append(short_call(stock_price, int(sp), int(Price)))
    	if selectedStrategy == "short_put": 
    		payoff.append(short_put(stock_price, int(sp), int(Price)))

    data = []

    for i in range(len(strike_price)):
        trace = go.Scatter(x=stock_price, y=payoff[i], mode='lines', name='Option Strike Price: '+str(strike_price[i]))
        data.append(trace)

    layout = {"title": "Option Payoff Chart for Nifty",'xaxis': dict(title='Stock Price'),'yaxis':dict(title='Profit/Loss')}
    fig = go.Figure(data=data, layout=layout)
    fig.add_vline(x=strike_price[0], line_width=2, line_dash="dash", line_color="green")
    fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")

    temp_data = pd.DataFrame(list(zip(stock_price, payoff[0])),
              columns=['stock_price','payoff'])
    temp_data['pnl'] = temp_data['payoff'] * 50
    filter_data = temp_data[temp_data['payoff'] > 0]
    filter_data.reset_index(inplace=True,drop=True)

    capital_required = round(int(Price)*int(lotsize),2)
    max_loss = min(temp_data['pnl'])
    if selectedStrategy == "long_call" or selectedStrategy == "short_put":
    	break_even = min(filter_data['stock_price'])
    else:
    	break_even = max(filter_data['stock_price'])
    max_gain = max(temp_data['pnl'])


    return jsonify(payoff_plot=fig.to_json(),capital_required=int(capital_required),max_loss=int(max_loss),break_even=int(break_even),max_gain=int(max_gain))

@app.route('/global_markets',methods=["GET"])
def global_markets():
    current_start_date = "2022-10-01"
    current_end_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")

    return render_template("global_markets.html", start_date = current_start_date, end_date = current_end_date)

@app.route('/update_global_data', methods=['POST'])
def update_global_data():

    current_start_date = request.get_json()["current_start_date"]
    current_end_date = request.get_json()["current_end_date"]
    print(current_end_date)
    print(current_start_date)
    figure = get_vix_data(current_start_date,current_end_date)
    # print(figure)
    # figure1 = get_s_and_p_market()
    # figure2 = get_global_market()

    last_30_days_data = get_global_market(current_start_date,current_end_date,db)

    print(last_30_days_data.head())

    dow_jones_data = last_30_days_data[last_30_days_data['Index'] == "Dow Jones"]
    nasdaq_data = last_30_days_data[last_30_days_data['Index'] == "Nasdaq"]
    s_and_p_data = last_30_days_data[last_30_days_data['Index'] == "S&P 500"]
    shanghai_data = last_30_days_data[last_30_days_data['Index'] == "Shanghai Composite"]
    shenzhen_data = last_30_days_data[last_30_days_data['Index'] == "Shenzhen Composite"]
    ftse_data = last_30_days_data[last_30_days_data['Index'] == "FTSE 100"]
    cac_data = last_30_days_data[last_30_days_data['Index'] == "CAC 40"]
    nikkei_data = last_30_days_data[last_30_days_data['Index'] == "Nikkei 225"]
    hang_seng_data = last_30_days_data[last_30_days_data['Index'] == "Hang Seng"]


    dow_jones_data.reset_index(inplace=True,drop=True)
    nasdaq_data.reset_index(inplace=True,drop=True)
    s_and_p_data.reset_index(inplace=True,drop=True)
    shanghai_data.reset_index(inplace=True,drop=True)
    shenzhen_data.reset_index(inplace=True,drop=True)
    ftse_data.reset_index(inplace=True,drop=True)
    cac_data.reset_index(inplace=True,drop=True)
    nikkei_data.reset_index(inplace=True,drop=True)
    hang_seng_data.reset_index(inplace=True,drop=True)

    trace_1 = go.Candlestick(x=dow_jones_data['Date'].tolist(),open=dow_jones_data['Open'].tolist(),high=dow_jones_data['High'].tolist(),low=dow_jones_data['Low'].tolist(),close=dow_jones_data['Close'].tolist(),name="dow_jones_data")
    trace_2 = go.Candlestick(x=nasdaq_data['Date'].tolist(),open=nasdaq_data['Open'].tolist(),high=nasdaq_data['High'].tolist(),low=nasdaq_data['Low'].tolist(),close=nasdaq_data['Close'].tolist(),name="nasdaq_data")
    trace_3 = go.Candlestick(x=s_and_p_data['Date'].tolist(),open=s_and_p_data['Open'].tolist(),high=s_and_p_data['High'].tolist(),low=s_and_p_data['Low'].tolist(),close=s_and_p_data['Close'].tolist(),name="s_and_p_data")
    trace_4 = go.Candlestick(x=shanghai_data['Date'].tolist(),open=shanghai_data['Open'].tolist(),high=shanghai_data['High'].tolist(),low=shanghai_data['Low'].tolist(),close=shanghai_data['Close'].tolist(),name="shanghai_data")
    trace_5 = go.Candlestick(x=shenzhen_data['Date'].tolist(),open=shenzhen_data['Open'].tolist(),high=shenzhen_data['High'].tolist(),low=shenzhen_data['Low'].tolist(),close=shenzhen_data['Close'].tolist(),name="shenzhen_data")
    trace_6 = go.Candlestick(x=ftse_data['Date'].tolist(),open=ftse_data['Open'].tolist(),high=ftse_data['High'].tolist(),low=ftse_data['Low'].tolist(),close=ftse_data['Close'].tolist(),name="ftse_data")
    trace_7 = go.Candlestick(x=cac_data['Date'].tolist(),open=cac_data['Open'].tolist(),high=cac_data['High'].tolist(),low=cac_data['Low'].tolist(),close=cac_data['Close'].tolist(),name="dow_jones_data")
    trace_8 = go.Candlestick(x=nikkei_data['Date'].tolist(),open=nikkei_data['Open'].tolist(),high=nikkei_data['High'].tolist(),low=nikkei_data['Low'].tolist(),close=nikkei_data['Close'].tolist(),name="nikkei_data")
    trace_9 = go.Candlestick(x=hang_seng_data['Date'].tolist(),open=hang_seng_data['Open'].tolist(),high=hang_seng_data['High'].tolist(),low=hang_seng_data['Low'].tolist(),close=hang_seng_data['Close'].tolist(),name="hang_seng_data")

    data_1 = [trace_1]
    data_2 = [trace_2]
    data_3 = [trace_3]
    data_4 = [trace_4]
    data_5 = [trace_5]
    data_6 = [trace_6]
    data_7 = [trace_7]
    data_8 = [trace_8]
    data_9 = [trace_9]

    layout_1 = {"title": "Dow Jones",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_2 = {"title": "Nasdaq",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_3 = {"title": "S&P 500",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_4 = {"title": "Shanghai Composite",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_5 = {"title": "Shenzhen Composite",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_6 = {"title": "FTSE 100",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_7 = {"title": "CAC 40",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_8 = {"title": "Nikkei 225",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    layout_9 = {"title": "Hang Seng",'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    
    fig_1 = go.Figure(dict(data=data_1, layout=layout_1))
    fig_2 = go.Figure(dict(data=data_2, layout=layout_2))
    fig_3 = go.Figure(dict(data=data_3, layout=layout_3))
    fig_4 = go.Figure(dict(data=data_4, layout=layout_4))
    fig_5 = go.Figure(dict(data=data_5, layout=layout_5))
    fig_6 = go.Figure(dict(data=data_6, layout=layout_6))
    fig_7 = go.Figure(dict(data=data_7, layout=layout_7))
    fig_8 = go.Figure(dict(data=data_8, layout=layout_8))
    fig_9 = go.Figure(dict(data=data_9, layout=layout_9))

    response_data = {
        "vix_plot": figure.to_html(),
        "dow_jones_plot": fig_1.to_html(),
        "nasdaq_plot" : fig_2.to_html(),
        "s_and_p_plot" : fig_3.to_html(),
        "shanghai_plot" : fig_4.to_html(),
        "shenzhen_plot" : fig_5.to_html(),
        "ftse_plot" : fig_6.to_html(),
        "cac_plot" : fig_7.to_html(),
        "nikkei_plot" : fig_8.to_html(),
        "hang_seng_plot" : fig_9.to_html()
    }


    return jsonify(response_data)

@app.route('/paper_trading')
def paper_trading():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('paper_trading.html', current_date=current_date)

@app.route('/get_candle_stick_data', methods=['POST'])
def get_candle_stick_data():
    date_selected = request.get_json()["selectedDate"]

    if date_selected == "":
    	date_selected = '2023-01-23'
    print(date_selected)

    
    
    sql = "SELECT distinct cast(Datetime as timestamp) as Datetime,Strategy,Stock,current_script,Signal,round(cast(Value as float64),2) as Value,buy_probability,sell_probability,round(cast(Target as float64),2) as Target,round(cast(StopLoss as float64),2) as StopLoss,Strike_Buy_Price FROM `ferrous-module-376519.Titania.new_candle_stick_signals` where date(cast(Datetime as timestamp)) = '" + str(date_selected) + "' order by cast(Datetime as timestamp) asc"

    print(sql)

    df = pandas_gbq.read_gbq(sql, project_id='ferrous-module-376519',credentials=credentials)

    if len(df) > 0 :
        df['Datetime'] = df['Datetime'].astype(str)
        df['Link'] = ''

        for idx in range(0,len(df)):
        	link_url = '<a href="#" data-smartapi="smartapi_key" data-exchange="NFO" data-tradingsymbol="'+str(df.loc[idx,"current_script"])+'" data-transactiontype="BUY"  data-quantity="1" data-price="'+str(df.loc[idx,"Strike_Buy_Price"]) +'" data-producttype="INTRADAY" data-ordertype="LIMIT">Buy Option</a>' 
        	df.loc[idx,'Link'] = link_url

    data = {"candle_stick_data": df.to_dict(orient='records')}


    collection = db["paper_trading_orders_place"]    
    paper_trading_orders_place = collection.find({"execution_date":str(date_selected)})
    paper_trading_orders_place =  pd.DataFrame(list(paper_trading_orders_place))

    options = ['Limit Order Placed', 'Buy Successful'] 
    print("paper_trading_orders_place")
    print(paper_trading_orders_place)

    completed_data = pd.DataFrame()
    open_data = pd.DataFrame()
    target_data = pd.DataFrame()
    stoploss_data = pd.DataFrame()

    if len(paper_trading_orders_place) > 0:
        completed_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Order Completed']
        open_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'].isin(options)]
        target_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Target Placed']
        stoploss_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Stoploss Placed']

        if len(completed_data) > 0:
            completed_data.reset_index(inplace=True,drop=True)
            for idx in range(0,len(completed_data)):
                print(idx)
                completed_data.loc[idx,"PNL"] = (float(completed_data.loc[idx,"premium_Target"]) - float(completed_data.loc[idx,"Strike_Buy_Price"]))*25 if (str(completed_data.loc[idx,"target_order_id"]) == str(completed_data.loc[idx,"final_order_id"])) else -(float(completed_data.loc[idx,"Strike_Buy_Price"]) - float(completed_data.loc[idx,"premium_StopLoss"]))*25

            completed_data = completed_data[['Strategy','Stock','Datetime','buy_probability','sell_probability','current_script','PNL']]
            completed_data['PNL'] = completed_data['PNL'].round(2)

        if len(open_data) > 0:
            open_data.reset_index(inplace=True,drop=True)
            open_data = open_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            open_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])

        if len(target_data) > 0:
            target_data.reset_index(inplace=True,drop=True)
            target_data = target_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            target_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])

        if len(stoploss_data) > 0:
            stoploss_data.reset_index(inplace=True,drop=True)
            stoploss_data = stoploss_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            stoploss_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])

    if not completed_data.empty:
        completed_data = completed_data.sort_values(by='Datetime')

    paper_data = {"completed_data": completed_data.to_dict(orient='records'),
              "open_data": open_data.to_dict(orient='records'),
              "target_data": target_data.to_dict(orient='records'),
              "stoploss_data": stoploss_data.to_dict(orient='records'),
              }

    # Chart 1: Bar chart - PNL distribution per strategy

    # Check if completed_data DataFrame is not empty
    if not completed_data.empty:
        grouped_data = completed_data.groupby("Strategy")["PNL"].sum().reset_index()

        chart1 = go.Figure()

        for idx, row in grouped_data.iterrows():
            color = "red" if row["PNL"] < 0 else "green"
            chart1.add_trace(go.Bar(x=[row["Strategy"]], y=[row["PNL"]], name=row["Strategy"],
                                    marker_color=color, showlegend=False))

        chart1.update_layout(
            xaxis_title="Strategy",
            yaxis_title="Profit and Loss",
            plot_bgcolor='rgba(240, 240, 240, 0.05)',
            xaxis=dict(
                tickfont=dict(size=12),
                titlefont=dict(size=14),
            ),
            yaxis=dict(
                tickfont=dict(size=12),
                titlefont=dict(size=14),
            ),
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="black",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        # chart1 = px.bar(completed_data, x="Strategy", y="PNL", labels={"PNL": "Profit and Loss"},
        #                 color_discrete_sequence=["red" if value < 0 else "green" for value in completed_data["PNL"]])
    else:
        # Create an empty chart with the appropriate labels
        chart1 = go.Figure(data=[go.Bar(x=[], y=[])])
        chart1.update_layout(
            xaxis_title="Strategy",
            yaxis_title="Profit and Loss",
        )

    # chart1 = px.bar(completed_data, x="Strategy", y="PNL", labels={"PNL": "Profit and Loss"})
    chart1_json = json.loads(chart1.to_json())

    # Chart 2: Pie chart - Distribution of conclusion types
    conclusion_counts = pd.Series({
        "completed": len(completed_data),
        "open": len(open_data),
        "target": len(target_data),
        "stoploss": len(stoploss_data)
    })
    chart2 = px.pie(names=conclusion_counts.index, values=conclusion_counts.values)
    chart2_json = json.loads(chart2.to_json())


    if not completed_data.empty:
        

        # Calculate the cumulative sum of PNL values
        completed_data['Cumulative_PNL'] = completed_data['PNL'].cumsum()

        # Calculate the percentage change in Cumulative PNL at every point
        # completed_data['Percentage_Change'] = completed_data['PNL'].pct_change().fillna(0) * 100

        chart_3 = go.Figure()

        # Create area plot
        chart_3.add_trace(go.Scatter(x=completed_data["Datetime"], y=completed_data["Cumulative_PNL"],
                              mode='lines', fill='tozeroy', name='Cumulative P&L by Time'))

        # Add percentage change labels to each data point
        for index, row in completed_data.iterrows():
            # chart_3.add_trace(go.Scatter(x=[row["Datetime"]], y=[row["Cumulative_PNL"]],
            #                               mode='text', text=[f"{row['Percentage_Change']:.2f}%"], textposition="top center",
            #                               showlegend=False))
            chart_3.add_trace(go.Scatter(x=[row["Datetime"]], y=[row["Cumulative_PNL"]],
                                  mode='text', text=[f"{row['Cumulative_PNL']:.2f}"],
                                  textposition="top center", showlegend=False,
                                  textfont=dict(color='green' if row['Cumulative_PNL'] >= 0 else 'red')))

        chart_3.update_layout(
                xaxis_title="Time",
                yaxis_title="Cumulative Profit and Loss",
                plot_bgcolor='rgba(240, 240, 240, 0.05)',
                xaxis=dict(
                    tickfont=dict(size=12),
                    titlefont=dict(size=14),
                ),
                yaxis=dict(
                    tickfont=dict(size=12),
                    titlefont=dict(size=14),
                ),
                font=dict(
                    family="Arial, sans-serif",
                    size=14,
                    color="black",
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
            )

    else:
        # Create an empty chart with the appropriate labels
        chart_3 = go.Figure(data=[go.Scatter(x=[], y=[], mode='lines')])
        chart_3.update_layout(
            xaxis_title="Time",
            yaxis_title="Profit and Loss",
        )

    chart3_json = json.loads(chart_3.to_json())

    total_pnl = 0
    average_pnl_per_trade = 0
    num_completed_trades = 0 
    num_open_trades = 0 
    win_rate = 0

    # Check if completed_data DataFrame is not empty
    if not completed_data.empty:
        total_pnl = completed_data["PNL"].sum()
        average_pnl_per_trade = completed_data["PNL"].mean()
        num_completed_trades = len(completed_data)
        num_open_trades = len(open_data)
        win_rate = len(completed_data[completed_data["PNL"] > 0]) / num_completed_trades

    metrics = {
        "total_pnl": total_pnl,
        "average_pnl_per_trade": average_pnl_per_trade,
        "num_completed_trades": num_completed_trades,
        "num_open_trades": num_open_trades,
        "win_rate": win_rate
    }

    # Add charts and metrics to the response
    response_data = {
        "data": data,
        "paper_data": paper_data,
        "charts": {
            "chart1": chart1_json,
            "chart2": chart2_json,
            "chart3": chart3_json
        },
        "metrics": metrics
    }



    # print(paper_data)

    # print(data)

    return Response(json.dumps(response_data), content_type="application/json")


    # return jsonify(data=data,paper_data=paper_data)

@app.route('/demand_and_supply')
def demand_and_supply():
    current_date = datetime.now(timezone("Asia/Kolkata"))
    start_date = current_date - timedelta(days=30*4)
    return render_template('demand_and_supply_zone.html', start_date=start_date.strftime("%Y-%m-%d"),end_date = current_date.strftime("%Y-%m-%d"))


def supply_zone_detection(df,stock,df_supply_and_demand):
    for ind in range(1, df.shape[0]-1):
        if (df.iloc[ind-1]['Open'] < df.iloc[ind-1]['Close'] and # Green Candle
            (abs(df.iloc[ind-1]['Open'] - df.iloc[ind-1]['Close']) > 0.5 * (df.iloc[ind-1]['High'] - df.iloc[ind-1]['Low'])) and # Im Balance Candle
            (abs(df.iloc[ind]['Open'] - df.iloc[ind]['Close']) <= 0.3 * (df.iloc[ind]['High'] - df.iloc[ind]['Low'])) and
            (df.iloc[ind+1]['Open'] > df.iloc[ind+1]['Close']) and # Red Candle
            (abs(df.iloc[ind+1]['Open'] - df.iloc[ind+1]['Close']) > 0.5 * (df.iloc[ind+1]['High'] - df.iloc[ind+1]['Low']))
           ):

            df_supply_and_demand.loc[ind,'stock'] = stock
            df_supply_and_demand.loc[ind,'pattern'] = "Supply Reversal Pattern(R-B-D)"
            df_supply_and_demand.loc[ind,'Date'] = df.iloc[ind]['Date']
            df_supply_and_demand.loc[ind,'zone_1'] = round(df.iloc[ind]['Low'],2) 
            # df_supply_and_demand.loc[ind,'zone_2'] = round(max(df.iloc[ind]['Open'],df.iloc[ind]['Close']),2)
            df_supply_and_demand.loc[ind,'zone_2'] = round(df.iloc[ind]['High'],2)

            if(df.iloc[ind+1]['Open'] > df.iloc[ind]['Open']):
                df_supply_and_demand.loc[ind,'strength'] = "Strong"
            else:
                df_supply_and_demand.loc[ind,'strength'] = "Normal"

        elif ((df.iloc[ind-1]['Open'] > df.iloc[ind-1]['Close']) and # Red Candle
              (abs(df.iloc[ind-1]['Open'] - df.iloc[ind-1]['Close']) > 0.5*(df.iloc[ind-1]['High'] - df.iloc[ind-1]['Low'])) and # Im-Balance Candle
              (abs(df.iloc[ind]['Open'] - df.iloc[ind]['Close']) <= 0.3*(df.iloc[ind]['High'] - df.iloc[ind]['Low'])) and
              (df.iloc[ind+1]['Open'] > df.iloc[ind+1]['Close']) and # Red Candle
              (abs(df.iloc[ind+1]['Open'] - df.iloc[ind+1]['Close']) > 0.5*(df.iloc[ind+1]['High'] - df.iloc[ind+1]['Low']))  # Im-Balance Candle
             ):

            df_supply_and_demand.loc[ind,'stock'] = stock
            df_supply_and_demand.loc[ind,'pattern'] = "Supply Continuous Pattern(D-B-D)"
            df_supply_and_demand.loc[ind,'Date'] = df.iloc[ind]['Date']
            df_supply_and_demand.loc[ind,'zone_1'] = round(df.iloc[ind]['Low'],2)
            # df_supply_and_demand.loc[ind,'zone_2'] = round(max(df.iloc[ind]['Open'],df.iloc[ind]['Close']),2)
            df_supply_and_demand.loc[ind,'zone_2'] = round(df.iloc[ind]['High'],2)

            if(df.iloc[ind+1]['Open'] < df.iloc[ind]['Open']):
                df_supply_and_demand.loc[ind,'strength'] = "Strong"
            else:
                df_supply_and_demand.loc[ind,'strength'] = "Normal"
                
    return df_supply_and_demand

def demand_zone_detection(df,stock,df_supply_and_demand):
    for ind in range(1, df.shape[0]-1):
        if ((df.iloc[ind-1]['Open'] > df.iloc[ind-1]['Close']) and
            (abs(df.iloc[ind-1]['Open'] - df.iloc[ind-1]['Close']) > 0.5 * (df.iloc[ind-1]['High'] - df.iloc[ind-1]['Low'])) and
            (abs(df.iloc[ind]['Open'] - df.iloc[ind]['Close']) <= 0.3 * (df.iloc[ind]['High'] - df.iloc[ind]['Low'])) and
            (df.iloc[ind+1]['Open'] < df.iloc[ind+1]['Close']) and # Green Candle
            (abs(df.iloc[ind+1]['Open'] - df.iloc[ind+1]['Close']) > 0.5 * (df.iloc[ind+1]['High'] - df.iloc[ind+1]['Low']))
           ):

            df_supply_and_demand.loc[ind,'stock'] = stock
            df_supply_and_demand.loc[ind,'pattern'] = "Demand Reversal Pattern(D-B-R)"
            df_supply_and_demand.loc[ind,'Date'] = df.iloc[ind]['Date']
            df_supply_and_demand.loc[ind,'zone_1'] = round(df.iloc[ind]['High'],2)
            # df_supply_and_demand.loc[ind,'zone_2'] = round(min(df.iloc[ind]['Open'],df.iloc[ind]['Close']),2)
            df_supply_and_demand.loc[ind,'zone_2'] = round(df.iloc[ind]['Low'],2)

            if(df.iloc[ind+1]['Open'] > df.iloc[ind]['Open']):
                df_supply_and_demand.loc[ind,'strength'] = "Strong"
            else:
                df_supply_and_demand.loc[ind,'strength'] = "Normal"

        elif ((df.iloc[ind-1]['Open'] < df.iloc[ind-1]['Close']) and # Green Candle
              (abs(df.iloc[ind-1]['Open'] - df.iloc[ind-1]['Close']) > 0.5 * (df.iloc[ind-1]['High'] - df.iloc[ind-1]['Low'])) and # Im-Balance Candle
              (abs(df.iloc[ind]['Open'] - df.iloc[ind]['Close']) <= 0.3 * (df.iloc[ind]['High'] - df.iloc[ind]['Low'])) and
              (df.iloc[ind+1]['Open'] < df.iloc[ind+1]['Close']) and # Green Candle
              (abs(df.iloc[ind+1]['Open'] - df.iloc[ind+1]['Close']) > 0.5 * (df.iloc[ind+1]['High'] - df.iloc[ind+1]['Low']))  # Im-Balance Candle
             ):

            df_supply_and_demand.loc[ind,'stock'] = stock
            df_supply_and_demand.loc[ind,'pattern'] = "Demand Continuous Pattern(R-B-R)"
            df_supply_and_demand.loc[ind,'Date'] = df.iloc[ind]['Date']
            df_supply_and_demand.loc[ind,'zone_1'] = round(df.iloc[ind]['High'],2)
            # df_supply_and_demand.loc[ind,'zone_2'] = round(min(df.iloc[ind]['Open'],df.iloc[ind]['Close']),2)
            df_supply_and_demand.loc[ind,'zone_2'] = round(df.iloc[ind]['Low'],2)

            if(df.iloc[ind+1]['Open'] > df.iloc[ind]['Open']):
                df_supply_and_demand.loc[ind,'strength'] = "Strong"
            else:
                df_supply_and_demand.loc[ind,'strength'] = "Normal"


@app.route('/get_demand_latest', methods=['POST'])
def get_demand_latest():
    start_date = request.get_json()["selectedStartDate"]
    end_date = request.get_json()["selectedEndDate"]

    df_supply_and_demand_final = pd.DataFrame(columns=["stock", "pattern", "strength", "Date", "zone_1", "zone_2"])
    current_dir = os.getcwd()

    print(current_dir)

    nifty_df = pd.read_csv("Nifty50_Stocks.csv")

    for idx in range(0,len(nifty_df)):
        stock = nifty_df.loc[idx,"Yahoo Symbol"]
        print(stock)
        # Download the data from Yahoo Finance
        data = yf.download(stock, start=start_date, end=end_date)
        data.reset_index(inplace=True)
        # Print the downloaded data
        print(data)
        
        df_supply_and_demand = pd.DataFrame(columns=["stock", "pattern", "strength", "Date", "zone_1", "zone_2"])
        
        supply_zone_df = supply_zone_detection(data,stock,df_supply_and_demand)
        
        if supply_zone_df is not None and len(supply_zone_df) > 0:
            df_supply_and_demand_final = pd.concat([df_supply_and_demand_final, supply_zone_df], axis=0, ignore_index=True)
        
        demand_zone_df = demand_zone_detection(data,stock,df_supply_and_demand)
        
        if demand_zone_df is not None and len(demand_zone_df) > 0:
            df_supply_and_demand_final = pd.concat([df_supply_and_demand_final, demand_zone_df], axis=0, ignore_index=True)
            
        if len(df_supply_and_demand_final) > 0 :
            print(df_supply_and_demand_final)
            df_supply_and_demand_final.reset_index(inplace=True,drop=True)
            

    if len(df_supply_and_demand_final) > 0 :
        df_supply_and_demand_final["Voided_Time"] = ""
        df_supply_and_demand_final["Percentage Change"]= 0

    for ind in range(df_supply_and_demand_final.shape[0]):
        stock = df_supply_and_demand_final.loc[ind, "stock"]
        call_date = df_supply_and_demand_final.loc[ind, "Date"]
        call_date = pd.to_datetime(call_date).date()
        print(stock)

        nextWorkingDay = (pd.to_datetime(call_date) + BDay(1)).date()
        nextWorkingDay = (pd.to_datetime(nextWorkingDay) + BDay(1)).date()

        try:
            if (nextWorkingDay - pd.to_datetime("today").date()).days <= -1:
                curr_stock_data = yf.download(stock, start=nextWorkingDay, end=pd.to_datetime("today")+pd.DateOffset(1))

                curr_stock_data = curr_stock_data.reset_index()

                max_zone = max(df_supply_and_demand_final.loc[ind, "zone_1"], df_supply_and_demand_final.loc[ind, "zone_2"])
                min_zone = min(df_supply_and_demand_final.loc[ind, "zone_1"], df_supply_and_demand_final.loc[ind, "zone_2"])

                df_supply_and_demand_final.loc[ind, "fit"] = "Active"


                current_close = curr_stock_data.tail(1)["Close"].values[0]

                if (df_supply_and_demand_final.loc[ind, "pattern"] == "Supply Reversal Pattern(R-B-D)") or (
                        df_supply_and_demand_final.loc[ind, "pattern"] == "Supply Continuous Pattern(D-B-D)"):

                    df_supply_and_demand_final.loc[ind, "Percentage Change"] = round(
                        (((df_supply_and_demand_final.loc[ind, "zone_1"] - current_close) / df_supply_and_demand_final.loc[ind, "zone_1"]) * 100), 2)

                    for row_ind in range(curr_stock_data.shape[0]):
                        if curr_stock_data.loc[row_ind, "Close"] > max_zone:
                            df_supply_and_demand_final.loc[ind, "fit"] = "Voided"
                            df_supply_and_demand_final.loc[ind, "Voided_Time"] = curr_stock_data.loc[row_ind, "Date"]
                            break

                else:
                    df_supply_and_demand_final.loc[ind, "Percentage Change"] = round(
                        (((current_close - df_supply_and_demand_final.loc[ind, "zone_1"]) / df_supply_and_demand_final.loc[ind, "zone_1"]) * 100), 2)

                    for row_ind in range(curr_stock_data.shape[0]):
                        if curr_stock_data.loc[row_ind, "Close"] < min_zone:
                            df_supply_and_demand_final.loc[ind, "fit"] = "Voided"
                            df_supply_and_demand_final.loc[ind, "Voided_Time"] = curr_stock_data.loc[row_ind, "Date"]
                            break

            else:
                df_supply_and_demand_final.loc[ind, "fit"] = "Active"

        except Exception as e:
            print("error for :")
            print(stock)

    print(df_supply_and_demand_final)

    filtered_df = df_supply_and_demand_final[(df_supply_and_demand_final['strength'] == 'Strong') & 
                                          (df_supply_and_demand_final['fit'] == 'Active') & 
                                          (df_supply_and_demand_final['Voided_Time']=="")]

    voided_df = df_supply_and_demand_final[(df_supply_and_demand_final['Voided_Time']!="")]

    filtered_df = filtered_df.sort_values(by="Date", ascending=False)
    filtered_df.reset_index(inplace=True,drop=True)

    voided_df = voided_df.sort_values(by="Date", ascending=False)
    voided_df.reset_index(inplace=True,drop=True)

    print(df_supply_and_demand_final)
    print(filtered_df)
    print(voided_df)

    final_data = {"total_stocks":df_supply_and_demand_final.to_dict(),
                    "active_stocks": filtered_df.to_dict(),
                    "voided_stocks":voided_df.to_dict()}

    return jsonify(final_data=final_data)

@app.route('/us_market')
def us_market():
    current_date = datetime.now().strftime("%Y-%m-%d")
    return render_template('us_paper_trading.html', current_date=current_date)

@app.route('/get_us_candle_stick_data', methods=['POST'])
def get_us_candle_stick_data():
    date_selected = request.get_json()["selectedDate"]

    if date_selected == "":
    	date_selected = '2023-01-23'
    print(date_selected)

    collection = db2["final_orders_raw_data"]    
    final_orders_raw_data = collection.find({"execution_date":str(date_selected)})

    final_orders_raw_data =  pd.DataFrame(list(final_orders_raw_data))

    if len(final_orders_raw_data)>0:
    	final_orders_raw_data = final_orders_raw_data[['Strategy', 'Stock', 'Signal', 'Datetime', 'Value','buy_probability', 'sell_probability',
       'StopLoss', 'Target', 'Qty', 'expiry','Spot_Price', 'Strike_Buy_Price', 'premium_StopLoss', 'premium_Target']]
    	final_orders_raw_data['buy_probability'] = final_orders_raw_data['buy_probability'].fillna(0)
    	final_orders_raw_data['sell_probability'] = final_orders_raw_data['sell_probability'].fillna(0)
    	final_orders_raw_data['Value'] = final_orders_raw_data['Value'].round(2)
    	final_orders_raw_data['buy_probability'] = final_orders_raw_data['buy_probability'].round(2)
    	final_orders_raw_data['sell_probability'] = final_orders_raw_data['sell_probability'].round(2)
    	final_orders_raw_data['StopLoss'] = final_orders_raw_data['StopLoss'].round(2)
    	final_orders_raw_data['Target'] = final_orders_raw_data['Target'].round(2)

    else:
    	final_orders_raw_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Signal', 'Datetime', 'Value','buy_probability', 'sell_probability',
       'StopLoss', 'Target', 'Qty', 'expiry','Spot_Price', 'Strike_Buy_Price', 'premium_StopLoss', 'premium_Target'])

    print(final_orders_raw_data)

    collection = db2["us_paper_trading_orders_place"]    
    paper_trading_orders_place = collection.find({"execution_date":str(date_selected)})
    paper_trading_orders_place =  pd.DataFrame(list(paper_trading_orders_place))

    options = ['Limit Order Placed', 'Buy Successful'] 
    print("paper_trading_orders_place")
    print(paper_trading_orders_place)

    completed_data = pd.DataFrame()
    open_data = pd.DataFrame()
    target_data = pd.DataFrame()
    stoploss_data = pd.DataFrame()

    if len(paper_trading_orders_place) > 0:
        completed_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Order Completed']
        open_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'].isin(options)]
        target_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Target Placed']
        stoploss_data = paper_trading_orders_place[paper_trading_orders_place['conclusion'] == 'Stoploss Placed']

        if len(completed_data) > 0:
            completed_data.reset_index(inplace=True,drop=True)
            for idx in range(0,len(completed_data)):
                print(idx)
                completed_data.loc[idx,"PNL"] = (float(completed_data.loc[idx,"premium_Target"]) - float(completed_data.loc[idx,"Strike_Buy_Price"]))*25 if (str(completed_data.loc[idx,"target_order_id"]) == str(completed_data.loc[idx,"final_order_id"])) else -(float(completed_data.loc[idx,"Strike_Buy_Price"]) - float(completed_data.loc[idx,"premium_StopLoss"]))*25

            completed_data = completed_data[['Strategy','Stock','Datetime','buy_probability','sell_probability','current_script','PNL']]
            completed_data['PNL'] = completed_data['PNL'].round(2)

        if len(open_data) > 0:
            open_data.reset_index(inplace=True,drop=True)
            open_data = open_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            open_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])

        if len(target_data) > 0:
            target_data.reset_index(inplace=True,drop=True)
            target_data = target_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            target_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])

        if len(stoploss_data) > 0:
            stoploss_data.reset_index(inplace=True,drop=True)
            stoploss_data = stoploss_data[['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp']]
        else:
            stoploss_data = pd.DataFrame(columns=['Strategy', 'Stock', 'Datetime','buy_probability', 'sell_probability', 'Strike_Buy_Price','current_script', 'token','Buy_timestamp'])


    paper_data = {"final_orders_raw_data":final_orders_raw_data.to_dict(),
            "completed_data": completed_data.to_dict(orient='records'),
              "open_data": open_data.to_dict(orient='records'),
              "target_data": target_data.to_dict(orient='records'),
              "stoploss_data": stoploss_data.to_dict(orient='records'),
              }

    # Create subplots with 5 rows and 1 column
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Strategy Signals", "Final Open Data", "Final Completed Data", "Target Placed Data", "Stoploss Placed Data"))

    # Add bar charts for buy and sell probabilities
    fig.add_trace(go.Bar(x=final_orders_raw_data['Datetime'], y=final_orders_raw_data['buy_probability'], name='Buy Probability'), row=1, col=1)
    fig.add_trace(go.Bar(x=final_orders_raw_data['Datetime'], y=final_orders_raw_data['sell_probability'], name='Sell Probability'), row=1, col=1)

    # Repeat the process for the other dataframes
    # For example, for open_data:
    fig.add_trace(go.Bar(x=open_data['Datetime'], y=open_data['buy_probability'], name='Buy Probability'), row=2, col=1)
    fig.add_trace(go.Bar(x=open_data['Datetime'], y=open_data['sell_probability'], name='Sell Probability'), row=2, col=1)

    # For completed_data, target_data, and stoploss_data, you can choose any relevant column as the y-axis value.
    # Here, I'm using the 'Value' column from the final_orders_raw_data DataFrame.

    # For completed_data:
    fig.add_trace(go.Bar(x=completed_data['Datetime'], y=final_orders_raw_data['Value'], name='Value'), row=3, col=1)

    # For target_data:
    fig.add_trace(go.Bar(x=target_data['Datetime'], y=final_orders_raw_data['Value'], name='Value'), row=4, col=1)

    # For stoploss_data:
    fig.add_trace(go.Bar(x=stoploss_data['Datetime'], y=final_orders_raw_data['Value'], name='Value'), row=5, col=1)

    # Customize the layout
    fig.update_layout(height=1000, title='Visualizing Trading Data')

    # Convert the chart to JSON format
    chart_json = fig.to_json()

    # Add the chart JSON to the response
    paper_data["chart"] = json.loads(chart_json)

    # print(paper_data)

    # paper_data = {"final_orders_raw_data": final_orders_raw_data.to_dict()}

    return jsonify(paper_data=paper_data)

@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))
        

if __name__ == '__main__':
    app.run(debug=True)
