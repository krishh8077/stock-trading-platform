
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from functools import wraps
import uuid
from aws import aws_manager
import traceback

app = Flask(__name__)
app.secret_key = 'stock-trading-platform-secret-key-2026'

# Stock data
STOCK_DATABASE = {
    'AAPL': {'name': 'Apple Inc.', 'price': 182.45, 'change': 2.35},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 140.82, 'change': -1.15},
    'MSFT': {'name': 'Microsoft Corp.', 'price': 380.61, 'change': 3.22},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 181.92, 'change': -0.88},
    'TSLA': {'name': 'Tesla Inc.', 'price': 238.45, 'change': 5.67},
    'META': {'name': 'Meta Platforms', 'price': 485.72, 'change': 8.34},
    'NFLX': {'name': 'Netflix Inc.', 'price': 247.18, 'change': -2.10},
    'NVIDIA': {'name': 'NVIDIA Corp.', 'price': 875.29, 'change': 12.45},
}

def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def log_exception(exc: Exception):
    tb = traceback.format_exc()
    with open('error.log', 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {str(exc)}\n")
        f.write(tb + "\n")
    print(tb)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template('signup.html', error='Username and password required')
            
            # Check if user exists
            user = aws_manager.dynamodb.get_user(username)
            if user:
                return render_template('signup.html', error='User already exists')
            
            # Create user with initial balance
            ok = aws_manager.dynamodb.create_user(username, password)
            if not ok:
                raise RuntimeError('Failed to create user in DynamoDB')
            session['username'] = username
            return redirect(url_for('dashboard'))
        except Exception as e:
            log_exception(e)
            return render_template('signup.html', error='Internal server error, check error.log')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Get user from DynamoDB
            user = aws_manager.dynamodb.get_user(username)
            
            if not user or user.get('password') != password:
                return render_template('login.html', error='Invalid credentials')
            
            session['username'] = username
            return redirect(url_for('dashboard'))
        except Exception as e:
            log_exception(e)
            return render_template('login.html', error='Internal server error, check error.log')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        username = session['username']
        user = aws_manager.dynamodb.get_user(username)
        if not user:
            return render_template('dashboard.html', error='User not found')

        balance = float(user.get('balance', 0.0))

        # Build portfolio list
        holdings_dict = aws_manager.dynamodb.get_portfolio(username) or {}
        portfolio = []
        portfolio_value = 0.0
        for symbol, data in holdings_dict.items():
            shares = int(data.get('shares', 0))
            avg_price = float(data.get('avg_price', 0.0))
            current_price = float(STOCK_DATABASE.get(symbol, {}).get('price', avg_price))
            position_value = shares * current_price
            gain_loss = position_value - (shares * avg_price)
            portfolio.append({
                'symbol': symbol,
                'shares': shares,
                'avg_price': avg_price,
                'current_price': current_price,
                'position_value': position_value,
                'gain_loss': gain_loss
            })
            portfolio_value += position_value

        total_value = balance + portfolio_value

        # Transactions
        transactions = aws_manager.dynamodb.get_transactions(username) or []

        return render_template(
            'dashboard.html',
            username=username,
            balance=balance,
            portfolio=portfolio,
            portfolio_value=portfolio_value,
            total_value=total_value,
            transactions=transactions
        )
    except Exception as e:
        log_exception(e)
        return render_template('dashboard.html', error='Internal server error, check error.log')

@app.route('/trade')
@login_required
def trade():
    username = session['username']
    user = aws_manager.dynamodb.get_user(username)
    stocks = list(STOCK_DATABASE.keys())
    return render_template('trade.html', stocks=stocks, user=user)

@app.route('/portfolio')
@login_required
def portfolio():
    username = session['username']
    portfolio = aws_manager.dynamodb.get_portfolio(username)
    user = aws_manager.dynamodb.get_user(username)
    return render_template('portfolio.html', portfolio=portfolio, user=user)

@app.route('/transactions')
@login_required
def transactions():
    username = session['username']
    txns = aws_manager.dynamodb.get_transactions(username)
    return render_template('transactions.html', transactions=txns)

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    if symbol not in STOCK_DATABASE:
        return jsonify({'error': 'Stock not found'}), 404
    return jsonify(STOCK_DATABASE[symbol])

@app.route('/api/stock/<symbol>/history')
def get_stock_history(symbol):
    timeframe = request.args.get('timeframe', '1m')
    
    if symbol not in STOCK_DATABASE:
        return jsonify({'error': 'Stock not found'}), 404
    
    # Simulated price data
    base_price = STOCK_DATABASE[symbol]['price']
    
    if timeframe == '5m':
        data = [base_price + (i - 5) * 0.5 for i in range(10)]
    elif timeframe == '1w':
        data = [base_price + (i - 7) * 2 for i in range(14)]
    else:  # 1m
        data = [base_price + (i - 15) * 5 for i in range(30)]
    
    return jsonify({'data': data, 'timeframe': timeframe})

@app.route('/api/buy', methods=['POST'])
@login_required
def buy_stock():
    username = session['username']
    data = request.json
    symbol = data.get('symbol')
    quantity = int(data.get('quantity', 0))
    price = float(data.get('price', 0))
    
    if not symbol or quantity <= 0:
        return jsonify({'error': 'Invalid input'}), 400
    
    # Get user and check balance
    user = aws_manager.dynamodb.get_user(username)
    total_cost = quantity * price
    
    if user['balance'] < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Update balance
    new_balance = user['balance'] - total_cost
    aws_manager.dynamodb.update_user_balance(username, new_balance)
    
    # Update portfolio
    portfolio = aws_manager.dynamodb.get_portfolio(username)
    if symbol in portfolio:
        portfolio[symbol]['shares'] += quantity
        portfolio[symbol]['avg_price'] = (portfolio[symbol]['avg_price'] * (portfolio[symbol]['shares'] - quantity) + price * quantity) / portfolio[symbol]['shares']
    else:
        portfolio[symbol] = {'shares': quantity, 'avg_price': price}
    
    aws_manager.dynamodb.update_portfolio(username, portfolio)
    
    # Add transaction
    transaction = {
        'transaction_id': str(uuid.uuid4()),
        'symbol': symbol,
        'type': 'BUY',
        'quantity': quantity,
        'price': price,
        'total': total_cost,
        'timestamp': datetime.now().isoformat()
    }
    aws_manager.dynamodb.add_transaction(username, transaction)
    
    # Send SNS notification
    aws_manager.sns.send_trade_notification(
        username,
        f"Buy Order Confirmation",
        f"Successfully bought {quantity} shares of {symbol} at ${price} each. Total: ${total_cost:.2f}"
    )
    
    return jsonify({'success': True, 'message': 'Buy order completed'})

@app.route('/api/sell', methods=['POST'])
@login_required
def sell_stock():
    username = session['username']
    data = request.json
    symbol = data.get('symbol')
    quantity = int(data.get('quantity', 0))
    price = float(data.get('price', 0))
    
    if not symbol or quantity <= 0:
        return jsonify({'error': 'Invalid input'}), 400
    
    # Get portfolio
    portfolio = aws_manager.dynamodb.get_portfolio(username)
    
    if symbol not in portfolio or portfolio[symbol]['shares'] < quantity:
        return jsonify({'error': 'Insufficient shares'}), 400
    
    # Update portfolio
    portfolio[symbol]['shares'] -= quantity
    if portfolio[symbol]['shares'] == 0:
        del portfolio[symbol]
    
    aws_manager.dynamodb.update_portfolio(username, portfolio)
    
    # Update balance
    total_proceeds = quantity * price
    user = aws_manager.dynamodb.get_user(username)
    new_balance = user['balance'] + total_proceeds
    aws_manager.dynamodb.update_user_balance(username, new_balance)
    
    # Add transaction
    transaction = {
        'transaction_id': str(uuid.uuid4()),
        'symbol': symbol,
        'type': 'SELL',
        'quantity': quantity,
        'price': price,
        'total': total_proceeds,
        'timestamp': datetime.now().isoformat()
    }
    aws_manager.dynamodb.add_transaction(username, transaction)
    
    # Send SNS notification
    aws_manager.sns.send_trade_notification(
        username,
        f"Sell Order Confirmation",
        f"Successfully sold {quantity} shares of {symbol} at ${price} each. Total: ${total_proceeds:.2f}"
    )
    
    return jsonify({'success': True, 'message': 'Sell order completed'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

