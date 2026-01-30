# Stock Trading Platform - AWS Deployment Guide

## Requirements
- AWS Account with EC2, DynamoDB, SNS, IAM access
- Git
- Python 3.8+

## Quick Setup Instructions

### 1. Create DynamoDB Tables (AWS Console)
Go to **DynamoDB** → **Create table** for each:

```
Table 1: StockTradingUsers
  - Partition Key: username (String)
  - Billing: Pay-per-request

Table 2: StockTradingPortfolios
  - Partition Key: username (String)
  - Billing: Pay-per-request

Table 3: StockTradingTransactions
  - Partition Key: username (String)
  - Sort Key: transaction_id (String)
  - Billing: Pay-per-request
```

### 2. Create SNS Topic (AWS Console)
Go to **SNS** → **Create topic**:
```
Name: stock-trading-notifications
Type: Standard
```
Subscribe to Email → Confirm email subscription

**Copy the Topic ARN** (you'll need it)

### 3. Create IAM Role for EC2 (AWS Console)
Go to **IAM** → **Create role**:
```
Trusted Entity: AWS Service → EC2
Permissions: 
  - AmazonDynamoDBFullAccess
  - AmazonSNSFullAccess
  - CloudWatchLogsFullAccess
Name: StockTradingEC2Role
```

### 4. Create Security Group (AWS Console)
Go to **EC2** → **Security Groups** → **Create**:
```
Name: stock-trading-app
Inbound Rules:
  - SSH (22) from 0.0.0.0/0
  - HTTP (80) from 0.0.0.0/0
  - Custom TCP (5000) from 0.0.0.0/0
```

### 5. Launch EC2 Instance (AWS Console)
Go to **EC2** → **Launch instances**:
```
AMI: Amazon Linux 2 (Free tier)
Instance Type: t3.micro
IAM Role: StockTradingEC2Role
Security Group: stock-trading-app
```

### 6. Connect via EC2 Connect (Browser)
1. Go to **EC2** → **Instances**
2. Select your instance
3. Click **Connect** → **EC2 Instance Connect** → **Connect**

### 7. Deploy Application

In EC2 terminal:

```bash
# Update system
sudo yum update -y

# Install dependencies
sudo yum install -y python3 python3-pip git

# Clone repository
git clone https://github.com/YOUR_USERNAME/stock-trading-platform.git
cd stock-trading-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Edit aws.py to set your SNS ARN
nano aws.py
```

Find line with:
```python
self.topic_arn = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:stock-trading-notifications'
```

**Replace `YOUR_ACCOUNT_ID` with your AWS Account ID** (from SNS topic ARN you copied)

Save: `Ctrl+X` → `Y` → `Enter`

### 8. Run Application

```bash
# Development
python3 app.py

# Production (with Gunicorn)
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### 9. Test
Open browser: `http://YOUR_EC2_PUBLIC_IP:5000`

---

## File Structure
```
stock-trading-platform/
├── app.py                 # Main Flask application
├── aws.py                 # AWS integration (DynamoDB, SNS)
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── static/               # CSS, JavaScript
└── templates/            # HTML templates
```

## Important
- **Only change**: SNS Topic ARN in `aws.py` line 25
- Everything else is pre-configured
- IAM Role handles AWS authentication
- No AWS credentials needed in code
