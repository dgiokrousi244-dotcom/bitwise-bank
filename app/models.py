from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class Admin(db.Model):
    """Admin user model"""
    __tablename__ = 'admin'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')  # admin, moderator, viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    """Client model"""
    __tablename__ = 'client'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    iban = db.Column(db.String(34), unique=True)
    bic_swift = db.Column(db.String(11))
    available_balance = db.Column(db.Float, default=0.0)
    kyc_status = db.Column(db.String(50), default='pending')  # pending, verified, rejected
    account_status = db.Column(db.String(50), default='active')  # active, suspended, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiaries = db.relationship('Beneficiary', backref='client', lazy=True, cascade='all, delete-orphan')
    savings_account = db.relationship('SavingsAccount', backref='client', uselist=False, cascade='all, delete-orphan')
    crypto_wallet = db.relationship('CryptoWallet', backref='client', uselist=False, cascade='all, delete-orphan')
    investment_portfolio = db.relationship('InvestmentPortfolio', backref='client', uselist=False, cascade='all, delete-orphan')
    credit_requests = db.relationship('CreditRequest', backref='client', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='client', lazy=True, cascade='all, delete-orphan')

class Beneficiary(db.Model):
    """Beneficiary model for SEPA transfers"""
    __tablename__ = 'beneficiary'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    iban = db.Column(db.String(34), nullable=False)
    bic_swift = db.Column(db.String(11))
    account_type = db.Column(db.String(50), default='personal')  # personal, business
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavingsAccount(db.Model):
    """Savings account model"""
    __tablename__ = 'savings_account'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    interest_rate = db.Column(db.Float, default=2.5)  # Annual interest rate
    total_saved = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Savings goals/objectives
    goals = db.relationship('SavingsGoal', backref='account', lazy=True, cascade='all, delete-orphan')

class SavingsGoal(db.Model):
    """Savings goals model"""
    __tablename__ = 'savings_goal'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    account_id = db.Column(db.String(36), db.ForeignKey('savings_account.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CryptoWallet(db.Model):
    """Crypto wallet model"""
    __tablename__ = 'crypto_wallet'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False, unique=True)
    bitcoin_balance = db.Column(db.Float, default=0.0)  # BTC
    ethereum_balance = db.Column(db.Float, default=0.0)  # ETH
    usdt_balance = db.Column(db.Float, default=0.0)  # USDT
    total_value_usd = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InvestmentPortfolio(db.Model):
    """Investment portfolio model"""
    __tablename__ = 'investment_portfolio'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False, unique=True)
    total_invested = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    total_profit_loss = db.Column(db.Float, default=0.0)
    roi_percentage = db.Column(db.Float, default=0.0)  # Return on Investment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    investments = db.relationship('Investment', backref='portfolio', lazy=True, cascade='all, delete-orphan')

class Investment(db.Model):
    """Individual investment model"""
    __tablename__ = 'investment'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    portfolio_id = db.Column(db.String(36), db.ForeignKey('investment_portfolio.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))  # stock, fund, bond, etc.
    amount_invested = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    profit_loss = db.Column(db.Float, default=0.0)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transaction(db.Model):
    """Transaction model"""
    __tablename__ = 'transaction'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # sepa, instant, deposit, withdrawal, crypto_buy, crypto_sell, investment_buy, investment_sell
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(50), default='pending')  # pending, completed, blocked, failed, cancelled
    description = db.Column(db.Text)
    recipient_name = db.Column(db.String(255))
    recipient_iban = db.Column(db.String(34))
    recipient_bic = db.Column(db.String(11))
    blocked_reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    executed_at = db.Column(db.DateTime)

class CreditRequest(db.Model):
    """Credit request model"""
    __tablename__ = 'credit_request'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'), nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    amount_approved = db.Column(db.Float)
    duration_months = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, default=5.0)  # Annual rate
    monthly_payment = db.Column(db.Float)
    purpose = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    repayment_schedule = db.relationship('RepaymentSchedule', backref='credit', lazy=True, cascade='all, delete-orphan')

class RepaymentSchedule(db.Model):
    """Repayment schedule model"""
    __tablename__ = 'repayment_schedule'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    credit_id = db.Column(db.String(36), db.ForeignKey('credit_request.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    principal = db.Column(db.Float, nullable=False)
    interest = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, overdue, partial
    paid_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ValidationCode(db.Model):
    """Validation code model"""
    __tablename__ = 'validation_code'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    code = db.Column(db.String(6), nullable=False, unique=True, index=True)
    code_type = db.Column(db.String(50), nullable=False)  # email, sms, 2fa, transaction, password_reset
    recipient = db.Column(db.String(255), nullable=False)  # email or phone
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=3)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired and self.attempts < self.max_attempts
