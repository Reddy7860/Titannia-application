from flask import render_template,flash,request, url_for, redirect,Flask,redirect, Response, session,jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.now()
    return render_template('index.html', now=now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']

    #     print(email)
    #     print(password)

    #     if request.form['email'] != 'admin@gmail.com' or request.form['password'] != 'admin':
    #         error = 'Invalid Credentials. Please try again.'
    #     else:
    #         return redirect('index.html')
    # else:
    #     # Render login page with empty form
    #     return render_template('login.html')
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/company_overview',methods=['GET', 'POST'])
def company_overview():
    if request.method == 'POST':
        stock_input = request.form['stock_input']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # Do something with the form data
        return render_template('company_overview.html', stock_input=stock_input, start_date=start_date, end_date=end_date)
    else:
        NSE_List = pd.read_csv("application/NSE_Stocks_List.csv")
        NSE_Tickers = NSE_List['Yahoo Symbol'].tolist()
        return render_template('company_overview.html',tickers=NSE_Tickers)
        

if __name__ == '__main__':
    app.run(debug=True)
