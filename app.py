from flask import Flask             #facilitate flask webserving
from flask import render_template, request   #facilitate jinja templating
from flask import session, redirect, url_for, make_response 
import os
import requests
import json
import db_builder
import weatherapi
import newsapi
import stockapi
from datetime import date
app = Flask(__name__)
app.secret_key = os.urandom(32)
genres = ["Business", "Entertainment", "General", "Health", "Science", "Sports", "Technology"]

cur_date = str(date.today())
if db_builder.new_day(cur_date):
    db_builder.update_date(cur_date)

# db_builder.update_date(cur_date)

@app.route('/')
def index():
    if 'username' in session:
        if db_builder.verify(session['username'], session['password']):
            return redirect("/home")
    return render_template('login.html') 

@app.route('/login', methods = ['GET','POST'])
def login():
    # print(request.form)
    username = request.form.get('username')
    password = request.form.get('password')
    if db_builder.verify(username,password):
        session['username'] = username
        session['password'] = password
        return redirect("/home")
    if request.form.get('create_acc_button') is not None:
        return render_template("create_account.html")
    response = make_response(render_template('error.html', msg="username or password is not correct"))
    return response

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    accounts = db_builder.get_table_list("User")
    if request.method == 'POST':
        userIn = request.form.get('username')
        passIn = request.form.get('password') 
        passConfirm = request.form.get('password2')

        if request.form.get('create_acc_button2') is None:
            return render_template("create_account.html")
        else:
            result = db_builder.add_account(userIn, passIn)
            if result != True:
                if result == -2:
                    return render_template("create_account.html", error_msg="Username/Password cannot be empty")
                elif db_builder.add_account(userIn, passIn) == -1:
                    return render_template("create_account.html",
                        error_msg= f"Account with username {userIn} already exists")
            if passIn != passConfirm:
                return render_template("create_account.html", error_msg="Passwords don't match")
            return render_template("sign_up_success.html")
    return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    if (verify_session()):
        username = session['username']
        weather_data = weatherapi.get_weather_data()
        articles = db_builder.get_from_genre("General")
        # Sam's code:
        # stocks = db_builder.get_stocks(username)
        # print("stocks: " + str(stocks))
        # stocks_with_price = []
        # for stock in stocks:
        #     print("stock: " + stock)
        #     stocks_with_price.append([stock, stockapi.get_price(stock)])
        # return render_template("home.html", articles=articles, genres=genres, weather=weather_data, stocks=stocks_with_price)
        # if 'stock_choice' in session:
        #     stocks = [[session['stock_choice'], stockapi.get_price(session['stock_choice'])]]
        # else:
        # stocks = [["aapl", stockapi.get_price("aapl")], ["tsla", stockapi.get_price("tsla")], ["googl", stockapi.get_price("googl")], ["amzn", stockapi.get_price("amzn")], ["meta", stockapi.get_price("meta")]]
        stocks = get_stocks(username)
        #print(f"stocks: {stocks}")
        #print(username)
        # stocks = db_builder.get_stocks(username)
        # for stock in stocks:
        #     stock.append(stockapi.get_price(stock[0]))
        return render_template("home.html", articles=articles, genres=genres, weather=weather_data, stocks=stocks)
        # username,sahjd, stocks --
        # "stockA,price,True;stockB,pr"
    else:
        return render_template("error.html", msg="session could not be verifited")

@app.route("/explore")
def explore():
    query = request.args.get("query")
    articles = []
    if query is not None:
        articles = newsapi.request_articles(query, 15)
    if(verify_session()):
        return render_template("explore.html", genres=genres, articles = articles)
    else:
        return render_template("error.html", msg="Session could not be verifited")  

@app.route("/topic")
def topic():
    if(verify_session()):
        username = session['username']
        weather_data = weatherapi.get_weather_data()
        topic = request.args.get("topic")
        articles = db_builder.get_from_genre(topic)
        # if 'stock_choice' in session:
        #     stocks = [[session['stock_choice'], stockapi.get_price(session['stock_choice'])]]
        # else:
        # stocks = [["aapl", stockapi.get_price("aapl")], ["tsla", stockapi.get_price("tsla")], ["googl", stockapi.get_price("googl")], ["amzn", stockapi.get_price("amzn")], ["meta", stockapi.get_price("meta")]]
        stocks = get_stocks(username)
        #stocks = # db_builder.get_stocks(username)
        return render_template("topic.html", articles=articles, topic=topic, genres=genres, weather = weather_data, stocks=stocks)
    else:
        return render_template("error.html", msg="session could not be verifited")

@app.route("/about")
def about():
    if(verify_session()):
        return render_template("about.html", genres=genres)
    else:
        return render_template("error.html", msg="session could not be verifited")

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if(verify_session()):
        username = session['username']
        if request.method == "POST":
            selected_user_stocks = request.form.getlist('True') + request.form.getlist('False')
            print(selected_user_stocks)
            db_builder.set_stocks(username, selected_user_stocks)
        # if request.method == 'POST':
        #     session['stock_choice']=(request.form.get('new_stock'))
        # if 'stock_choice' in session:
        #     print(session['stock_choice'])
        #     db_builder.add_stock(username, session['stock_choice'])
        # print(f"get_stocks: {get_stocks(username)}")
        # PROBLEM LINES:
        user_stocks = get_stocks(username)
        # print(user_stocks)
        # print(user_stocks)
        user_stocks = [user_stock.split(",") for user_stock in user_stocks]
        user_stocks = [user_stock[:-1] + [True if user_stock[-1] == 'True' else False] for user_stock in user_stocks]
        # print(user_stocks)
        # print(f"user_stocks: {user_stocks}")
        return render_template("profile.html", username=session['username'], genres=genres, user_stocks=user_stocks)
    else:
        return render_template("error.html", msg="session could not be verifited")
        
def verify_session():
    if 'username' in session and 'password' in session:
        if db_builder.verify(session['username'], session['password']):
            return True
    return False

def get_stocks(username):
    stocks = db_builder.get_stocks(username)
    # print(f"stocks_gs: [{stocks[0]}, ..., {stocks[-1]}]")
    index = 0
    for stock in stocks:
        stock = stock.split(",")
        if stock[-1] == 'True':
            stock.insert(-1, stockapi.get_price(stock[0]))
        stock = ",".join(stock)
        stocks[index] = stock
        index += 1
    # print(f"\nstocks w/ price: ['{stocks[0]}', '{stocks[1]}', '{stocks[2]}', '{stocks[3]}', '{stocks[4]}', '{stocks[5]}',..., '{stocks[-1]}'")
    # print(stocks)
    return stocks

