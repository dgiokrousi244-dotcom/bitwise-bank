from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import func

db = SQLAlchemy()

# ==================== ADMIN MODELS ====================

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='moderator')  # admin, moderator, viewer
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== CLIENT MODELS ====================

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    available_balance = db.Column(db.Float, default=0.0)
    iban = db.Column(db.String(34), unique=True)
    bic_swift = db.Column(db.String(11))
    kyc_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    account_status = db.Column(db.String(50), default='active')  # active, suspended, frozen
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiaries = db.relationship('Beneficiary', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    credit_requests = db.relationship('CreditRequest', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    savings_account = db.relationship('SavingsAccount', backref='client', uselist=False, cascade='all, delete-orphan')
    crypto_wallet = db.relationship('CryptoWallet', backref='client', uselist=False, cascade='all, delete-orphan')
    investment_portfolio = db.relationship('InvestmentPortfolio', backref='client', uselist=False, cascade='all, delete-orphan')

class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    iban = db.Column(db.String(34), nullable=False)
    bic_swift = db.Column(db.String(11), nullable=False)
    account_type = db.Column(db.String(50), default='personal')  # personal, business
    bank_name = db.Column(db.String(120))
    country = db.Column(db.String(50))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== ACCOUNT MODELS ====================

class SavingsAccount(db.Model):
    __tablename__ = 'savings_accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    goals = db.Column(JSON, default=list)  # [{name: "Vacation", target: 5000, current: 2000}]
    interest_rate = db.Column(db.Float, default=1.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CryptoWallet(db.Model):
    __tablename__ = 'crypto_wallets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    holdings = db.Column(JSON, default=dict)  # {BTC: 0.5, ETH: 2, USDT: 1000}
    wallet_address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InvestmentPortfolio(db.Model):
    __tablename__ = 'investment_portfolios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    total_value = db.Column(db.Float, default=0.0)
    assets = db.Column(JSON, default=list)  # [{name: "Apple", shares: 10, price: 150, value: 1500}]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== TRANSACTION MODELS ====================

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # sepa, instantaneous, deposit, withdrawal
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    recipient_name = db.Column(db.String(120))
    recipient_iban = db.Column(db.String(34))
    bic_swift = db.Column(db.String(11))
    status = db.Column(db.String(50), default='pending')  # pending, blocked, executed, completed, cancelled
    reference = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== CREDIT MODELS ====================

class CreditRequest(db.Model):
    __tablename__ = 'credit_requests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    amount_approved = db.Column(db.Float)
    duration_months = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, default=5.0)
    monthly_payment = db.Column(db.Float)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, active, completed
    purpose = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repayment_schedule = db.relationship('RepaymentSchedule', backref='credit', lazy='dynamic', cascade='all, delete-orphan')

class RepaymentSchedule(db.Model):
    __tablename__ = 'repayment_schedules'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    credit_id = db.Column(db.String(36), db.ForeignKey('credit_requests.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    principal = db.Column(db.Float, nullable=False)
    interest = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, overdue
    paid_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== VALIDATION CODE MODEL ====================

class ValidationCode(db.Model):
    __tablename__ = 'validation_codes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    code = db.Column(db.String(6), nullable=False)
    code_type = db.Column(db.String(50), nullable=False)  # email, sms, 2fa, transaction, password_reset
    email_or_phone = db.Column(db.String(120), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
