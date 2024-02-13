from app import *

def register_user(userID, username, balance):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, balance) VALUES (?, ?)', (username, balance))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_balance(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    balance = cursor.fetchone()
    conn.close()
    return balance

def update_user_balance(balance, userID):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (balance, userID))
    conn.commit()
    cursor.close()
    conn.close()

def get_portfolio(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT symbol, SUM(quantity) as total_quantity
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
    ''', (user_id,))
    portfolio = cursor.fetchall()
    conn.close()
    return portfolio

def get_stocks_owned(user_id, symbol):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(CASE WHEN transaction_type = 'BUY' THEN quantity ELSE -quantity END) as total_quantity
        FROM transactions
        WHERE user_id = ? AND symbol = ?
    ''', (user_id, symbol))
    stocks_owned = cursor.fetchone()[0]
    conn.close()
    return stocks_owned