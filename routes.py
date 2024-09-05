from flask import render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db, login_manager
from models import User, Stock
from flask_login import LoginManager
import yfinance as yf

# Helper functions
def fetch_latest_price(ticker):
    stock = yf.Ticker(ticker)
    latest_price = stock.history(period="1d")['Close'].iloc[-1]
    return latest_price

def fetch_forwardPE(ticker):
    stock = yf.Ticker(ticker)
    quote_table = stock.info
    forward_pe = quote_table.get('forwardPE')
    return forward_pe

def fetch_divyiled(ticker):
    stock = yf.Ticker(ticker)
    quote_table = stock.info
    div_yield = quote_table.get('dividendYield')
    # Check if div_yield is None, and return "-" if it is
    if div_yield is None:
        return "-"
    # If div_yield is a valid number, multiply by 100 to get the percentage
    return div_yield * 100

def calculate_returns(purchase_price, latest_price):
    return ((latest_price - purchase_price) / purchase_price) * 100

def calculate_portfolio_return(stocks_data):
    total_investment = sum(stock.purchase_price * stock.shares for stock in stocks_data)
    total_current_value = sum(stock.latest_price * stock.shares for stock in stocks_data)
    portfolio_return = ((total_current_value - total_investment) / total_investment) * 100
    return portfolio_return


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        ticker = request.form['ticker']
        purchase_price = float(request.form['purchase_price'])
        shares = int(request.form['num_shares'])
        
        latest_price = fetch_latest_price(ticker)
        return_performance = calculate_returns(purchase_price, latest_price)
        forward_pe = fetch_forwardPE(ticker)
        div_yield = fetch_divyiled(ticker)
        
        stock = Stock.query.filter_by(ticker=ticker, user_id=current_user.id).first()
        if stock:
            stock.purchase_price = purchase_price
            stock.shares = shares
            stock.latest_price = latest_price
            stock.return_performance = return_performance
            stock.forward_pe = forward_pe
            stock.div_yield = div_yield
        else:
            new_stock = Stock(
                ticker=ticker,
                purchase_price=purchase_price,
                shares=shares,
                latest_price=latest_price,
                return_performance=return_performance,
                forward_pe=forward_pe,
                div_yield=div_yield,
                user_id=current_user.id
            )
            db.session.add(new_stock)
        db.session.commit()
        return redirect(url_for('home'))
    
    stock_data = Stock.query.filter_by(user_id=current_user.id).all()

    # Update latest prices and recalculate return for each stock
    for stock in stock_data:
        stock.latest_price = fetch_latest_price(stock.ticker)
        stock.return_performance = calculate_returns(stock.purchase_price, stock.latest_price)
    
    db.session.commit()

    portfolio_return = calculate_portfolio_return(stock_data) if stock_data else 0
    return render_template('home.html', stocks=stock_data, portfolio_return=portfolio_return)

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    ticker = request.form['ticker']
    stock = Stock.query.filter_by(ticker=ticker, user_id=current_user.id).first()
    if stock:
        db.session.delete(stock)
        db.session.commit()
    return redirect(url_for('home'))