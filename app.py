# app.py

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import database
import market

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database initialization
DATABASE = 'trading_simulator.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET','POST'])
def welcome():
    create_table()

    if database.get_user(1):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        userID = 1
        database.register_user(name, userID)
        return redirect(url_for('index'))
    
    return render_template('welcome.html')

@app.route("/home")
def index():
    user_id = 1  # Change this to the logged-in user's ID
    user = database.get_user(user_id)
    portfolio = database.get_portfolio(user_id)
    print(user)
    print(portfolio)
    return render_template('index.html', user=user, portfolio=portfolio)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        balance = float(request.form['balance'])
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, balance) VALUES (?, ?)', (username, balance))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route("/search", methods=['GET', 'POST'])
def search():
    # Get the search term from the form
    search_term = request.form.get('searchTerm')

    # Perform any processing with the search term (e.g., fetch stock data)
    stocks = market.search_stocks(search_term)

    print("STocks: ")
    print(stocks)

    # For demonstration purposes, let's just display the search term
    return render_template('search.html', search_term=search_term, stocks=stocks)

@app.route('/buy', methods=['GET', 'POST'])
def buy():

    if request.method == 'POST':
        user_id = 1  # Change this to the logged-in user's ID
        symbol = request.form['symbol']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the user has enough balance
        user = database.get_user(user_id)
        if user[2] >= quantity * price:
            # Update user balance
            new_balance = user[2] - quantity * price
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))

            # Add a new buy transaction
            cursor.execute('INSERT INTO transactions (user_id, symbol, quantity, price, transaction_type) VALUES (?, ?, ?, ?, ?)',
                           (user_id, symbol, quantity, price, 'BUY'))

            conn.commit()
        else:
            return "Insufficient funds to complete the purchase"

        conn.close()
        return redirect(url_for('index'))

    return render_template('buy.html')

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        user_id = 1  # Change this to the logged-in user's ID
        symbol = request.form['symbol']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the user has enough stocks to sell
        stocks_owned = database.get_stocks_owned(user_id, symbol)
        if stocks_owned >= quantity:
            # Update user balance
            user = database.get_user(user_id)
            new_balance = user[2] + quantity * price
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))

            # Add a new sell transaction
            cursor.execute('INSERT INTO transactions (user_id, symbol, quantity, price, transaction_type) VALUES (?, ?, ?, ?, ?)',
                           (user_id, symbol, quantity, price, 'SELL'))

            conn.commit()
        else:
            return "You don't own enough stocks to complete the sale"

        conn.close()
        return redirect(url_for('index'))

    return render_template('sell.html')

from flask import render_template

@app.route('/stock_details/<symbol>')
def stock_details(symbol):
    # Fetch stock data based on the symbol
    # Replace this with your logic to get stock data
    stock_data = market.get_info(symbol)

    print("Stock Data: ")
    print(stock_data)

    # Render the stock details template with the stock data
    return render_template('stock.html', stock_data=stock_data)



if __name__ == '__main__':
    app.run(debug=True)
