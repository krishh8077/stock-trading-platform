"""
AWS Integration Module - Simplified for Stock Trading Platform
Only DynamoDB, SNS, and IAM role
"""

import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Convert DynamoDB Decimal to float"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

class DynamoDBHandler:
    """DynamoDB Operations"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.users_table = self.dynamodb.Table('StockTradingUsers')
        self.portfolios_table = self.dynamodb.Table('StockTradingPortfolios')
        self.transactions_table = self.dynamodb.Table('StockTradingTransactions')
    
    def create_user(self, username, password):
        """Create new user with initial balance"""
        try:
            timestamp = datetime.utcnow().isoformat()
            self.users_table.put_item(
                Item={
                    'username': username,
                    'password': password,
                    'balance': Decimal('10000.00'),
                    'created_at': timestamp
                }
            )
            # Create empty portfolio
            self.portfolios_table.put_item(
                Item={
                    'username': username,
                    'holdings': {}
                }
            )
            return True
        except ClientError as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, username):
        """Get user"""
        try:
            response = self.users_table.get_item(Key={'username': username})
            item = response.get('Item', None)
            if item:
                # Convert Decimal to float
                item['balance'] = float(item['balance'])
            return item
        except ClientError as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_balance(self, username, new_balance):
        """Update balance"""
        try:
            self.users_table.update_item(
                Key={'username': username},
                UpdateExpression='SET balance = :b',
                ExpressionAttributeValues={
                    ':b': Decimal(str(new_balance))
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating balance: {e}")
            return False
    
    def get_portfolio(self, username):
        """Get portfolio holdings"""
        try:
            response = self.portfolios_table.get_item(Key={'username': username})
            item = response.get('Item', {})
            holdings = item.get('holdings', {})
            # Convert Decimal to float
            for symbol in holdings:
                if 'avg_price' in holdings[symbol]:
                    holdings[symbol]['avg_price'] = float(holdings[symbol]['avg_price'])
            return holdings
        except ClientError as e:
            print(f"Error getting portfolio: {e}")
            return {}
    
    def update_portfolio(self, username, holdings):
        """Update portfolio holdings"""
        try:
            # Convert floats to Decimal for DynamoDB
            converted_holdings = {}
            for symbol, data in holdings.items():
                converted_holdings[symbol] = {
                    'shares': data['shares'],
                    'avg_price': Decimal(str(data['avg_price']))
                }
            
            self.portfolios_table.update_item(
                Key={'username': username},
                UpdateExpression='SET holdings = :h',
                ExpressionAttributeValues={
                    ':h': converted_holdings
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating portfolio: {e}")
            return False
    
    def add_transaction(self, username, transaction):
        """Add transaction record"""
        try:
            transaction['username'] = username
            transaction['price'] = Decimal(str(transaction['price']))
            transaction['total'] = Decimal(str(transaction['total']))
            
            self.transactions_table.put_item(Item=transaction)
            return True
        except ClientError as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_transactions(self, username):
        """Get all transactions for user"""
        try:
            response = self.transactions_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(username)
            )
            items = response.get('Items', [])
            # Convert Decimal to float
            for item in items:
                if 'price' in item:
                    item['price'] = float(item['price'])
                if 'total' in item:
                    item['total'] = float(item['total'])
            return items
        except ClientError as e:
            print(f"Error getting transactions: {e}")
            return []

class SNSHandler:
    """SNS Notifications"""
    
    def __init__(self):
        self.sns_client = boto3.client('sns', region_name='us-east-1')
        # CHANGE THIS SNS ARN ONLY - DO NOT CHANGE ANYTHING ELSE
        self.topic_arn = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications'
    
    def send_trade_notification(self, username, subject, message):
        """Send trade notification via SNS"""
        try:
            self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=f"[Stock Trading] {subject}",
                Message=f"User: {username}\n\n{message}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return True
        except ClientError as e:
            print(f"Error sending SNS notification: {e}")
            return False

class AWSManager:
    """Main AWS Manager"""
    
    def __init__(self):
        self.dynamodb = DynamoDBHandler()
        self.sns = SNSHandler()

# Global instance
aws_manager = AWSManager()
