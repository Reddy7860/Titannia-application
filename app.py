from flask import render_template,flash,request, url_for, redirect,Flask,redirect, Response, session,jsonify
from datetime import datetime
import pandas as pd
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

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

@app.route('/orders_preview')
def orders_preview():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('client_data_update.html', current_date=current_date)

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
	
	paper_data = {"technical_indicators": technical_indicators.to_dict()}

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
    

    figure = get_combined_chart(selectedOption,selectedDate,selectedLine)

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

    return jsonify(figure=figure.to_html())

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

    last_30_days_data = get_global_market(current_start_date,current_end_date)

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
    	df['Link'] = ''

    	for idx in range(0,len(df)):
    		link_url = '<a href="#" data-smartapi="smartapi_key" data-exchange="NFO" data-tradingsymbol="'+str(df.loc[idx,"current_script"])+'" data-transactiontype="BUY"  data-quantity="1" data-price="'+str(df.loc[idx,"Strike_Buy_Price"]) +'" data-producttype="INTRADAY" data-ordertype="LIMIT">Buy Option</a>' 
    		df.loc[idx,'Link'] = link_url

    data = {"candle_stick_data": df.to_dict()}


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


    paper_data = {"completed_data": completed_data.to_dict(),
    		 "open_data": open_data.to_dict(),
    		 "target_data": target_data.to_dict(),
    		 "stoploss_data": stoploss_data.to_dict(),
    		 }

    print(paper_data)


    return jsonify(data=data,paper_data=paper_data)

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

    nifty_df = pd.read_csv("application/Nifty50_Stocks.csv")

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

    paper_data = {"final_orders_raw_data": final_orders_raw_data.to_dict()}

    return jsonify(paper_data=paper_data)

@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))
        

if __name__ == '__main__':
    app.run(debug=True)
