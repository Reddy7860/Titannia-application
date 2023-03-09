from flask import render_template,flash,request, url_for, redirect,Flask,redirect, Response, session,jsonify
from datetime import datetime
import pandas as pd

app = Flask(__name__)


# Set secret key for session management
app.secret_key = "mysecretkey"

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
        NSE_List = pd.read_csv("application/NSE_Stocks_List.csv")
        NSE_Tickers = NSE_List['Yahoo Symbol'].tolist()
        return render_template('company_overview.html',tickers=NSE_Tickers)

@app.route('/orders_preview')
def orders_preview():
    current_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    return render_template('client_data_update.html', current_date=current_date)

@app.route('/logout')
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))
        

if __name__ == '__main__':
    app.run(debug=True)
