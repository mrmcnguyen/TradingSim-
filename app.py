# app.py


from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import database
import market
import time


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
            balance REAL NOT NULL DEFAULT 0.0
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            stock_price REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            stock_price REAL NOT NULL,
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
        database.register_user(userID, name, 1000)
        print("This ran")
        return redirect(url_for('index'))
   
    return render_template('welcome.html')


@app.route("/home")
def index():

    start_time = time.time()
    user_id = 1  # Change this to the logged-in user's ID
    user = database.get_user(user_id)
    portfolio = [list(stock) for stock in database.get_portfolio(user_id)]
   
    if portfolio is None:
        portfolio = [0]
    print(user)
    portfolioValue = 0
    PandL = 0
    percentageChange = 0

    stock_prices = {stock[0]: market.get_ticker_price(stock[0]) for stock in portfolio}

    # Calculate P&L
    for stock in portfolio:
        current_price = stock_prices[stock[0]]
        stock.append(round(current_price - stock[3], 2)*stock[1] if current_price > stock[3] else round(-(stock[3] - current_price),2)*stock[1] if current_price < stock[3] else 0)
        PandL += stock[4]
        stock_value = stock[1] * stock_prices[stock[0]]
        stock.append(stock_value)
        portfolioValue += stock_value
        stock.append(round((stock[5] - stock[2])/100, 2) if stock[5] > stock[2] else round(-(stock[2] - stock[5])/100, 2) if stock[2] > stock[5] else 0)
        percentageChange += stock[6]
    
    #top_movers = market.get_top_movers()
    print(portfolio)    

    # Record the end time
    end_time = time.time()

    # Calculate the runtime
    runtime = end_time - start_time
    print(f"Runtime: {runtime} seconds")

    return render_template('index.html', user=user, portfolio=portfolio, portfolioValue=portfolioValue, PandL=PandL, percentageChange=percentageChange)


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

    stocks = [{'symbol': stock.split(" - ")[0], 'symbolName': stock.split(" - ")[1]} for stock in stocks]

    print(stocks)
    return render_template('search.html', search_term=search_term, stocks=stocks)


@app.route('/buy/<ticker>', methods=['POST', 'GET'])
def buy(ticker):
    print("BUY FUNCTION RAN")
    stock_data = market.get_info(ticker)


    # Check if a form is submitted
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        order_type = request.form.get('orderType')


        # Connect to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()


        # Calculate total price (replace with your actual logic)
        ticker_price = market.get_ticker_price(ticker)
        total_price = market.calculate_price(ticker, quantity, order_type)


        userID = 1
        user_balance = database.get_user_balance(userID)[0]
        print(total_price)


        if user_balance < total_price:
            flash("Insufficient Funds.")
            return redirect(url_for('index'))

        existing_holding = database.get_holdings(ticker, userID)
        print(existing_holding)

        # If user already owns stock
        if existing_holding:
            new_quantity = existing_holding[3] + quantity
            new_total_price = existing_holding[4] + total_price

            print(new_total_price)
            cursor.execute('UPDATE Holdings SET quantity=?, price=?, stock_price=? WHERE id=?',
                           (new_quantity, new_total_price, ticker_price, existing_holding[0]))
        else:
            cursor.execute('INSERT INTO Holdings (user_id, symbol, quantity, price, stock_price, transaction_type) VALUES (?, ?, ?, ?, ?, ?)',
            (userID, ticker, quantity, total_price, ticker_price, 'BUY'))

        # Record transaction
        cursor.execute('INSERT INTO Transactions (user_id, symbol, quantity, price, stock_price, transaction_type) VALUES (?, ?, ?, ?, ?, ?)',
                (userID, ticker, quantity, total_price, ticker_price, 'BUY'))
       
        conn.commit()
        conn.close()

        remaining_balance = user_balance - total_price
        database.update_user_balance(remaining_balance, userID)

        # Store order details in session
        session['order_details'] = {
            'symbol': ticker,
            'quantity': quantity,
            'order_type': order_type,
            'total_price': total_price,
            'buying_power':remaining_balance
        }


        return render_template('buy.html', stock_data=stock_data, order_details=session['order_details'])
   
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

@app.route('/holdings')
def holdings():

    start_time = time.time()
    portfolio = [list(stock) for stock in database.get_portfolio(1)]
    PandL = 0
    percentageChange = 0
    
    portfolioValue = 0

    stock_prices = {stock[0]: market.get_ticker_price(stock[0]) for stock in portfolio}

    for stock in portfolio:
        current_price = stock_prices[stock[0]]
        stock.append(round(current_price - stock[3], 2)*stock[1] if current_price > stock[3] else round(-(stock[3] - current_price),2)*stock[1] if current_price < stock[3] else 0)
        stock_value = stock[1] * stock_prices[stock[0]]
        stock.append(stock_value)
        portfolioValue += stock[5]
        PandL += stock[4]
        stock.append(round((stock[5] - stock[2])/100, 2) if stock[5] > stock[2] else round(-(stock[2] - stock[5])/100, 2) if stock[2] > stock[5] else 0)
        percentageChange += stock[6]

    # Record the end time
    end_time = time.time()

    # Calculate the runtime
    runtime = end_time - start_time
    print(f"Runtime: {runtime} seconds")
    return render_template('holdings.html', portfolio=portfolio, portfolioValue=portfolioValue, PandL=PandL)

@app.route('/stock_details/<symbol>')
def stock_details(symbol):
    userID = 1
    # Fetch stock data based on the symbol
    # Replace this with your logic to get stock data
    stock_data = market.get_info(symbol)
    user_balance = database.get_user_balance(userID)

    print("Stock Data: ")
    print(stock_data)
    # Render the stock details template with the stock data
    return render_template('stock.html', stock_data=stock_data, user_balance=user_balance)


if __name__ == '__main__':
    app.run(debug=True)



