# Bitwise Bank - Admin Dashboard Backend

## 📋 Description

Backend API for Bitwise Bank administration panel, enabling complete management of:
- Client accounts and profiles
- Beneficiaries and transfers
- Credit requests and repayment schedules
- Transactions (SEPA, Instant, Crypto, Investments)
- Savings accounts and investment portfolios
- Validation codes

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/dgiokrousi244-dotcom/bitwise-bank.git
cd bitwise-bank

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run application
python run.py
```

API will be available at `http://localhost:5000/api/admin`

## 📦 Project Structure

```
bitwise-bank/
├── app/
│   ├── __init__.py           # Factory pattern
│   ├── extensions.py         # Extensions (DB, JWT)
│   ├── models.py             # 10 Database models
│   └── admin/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── auth.py       # Authentication
│           ├── clients.py    # Client management
│           ├── operations.py # Dashboard & operations
│           ├── credits.py    # Credit management
│           ├── transactions.py # Transaction management
│           └── codes.py      # Validation codes
├── config.py                 # Configuration
├── run.py                    # Entry point
├── requirements.txt          # Dependencies
├── .env.example              # Environment variables template
└── README.md
```

## 🗄️ Database Models

### Core Models

1. **Admin** - Administrator users with roles
2. **Client** - Bank clients with profiles
3. **Beneficiary** - SEPA beneficiaries
4. **Transaction** - All types of transactions
5. **CreditRequest** - Credit applications
6. **RepaymentSchedule** - Loan repayment schedules
7. **ValidationCode** - 2FA and verification codes

### Specialized Accounts

8. **SavingsAccount** - Savings with goals
9. **CryptoWallet** - BTC, ETH, USDT balances
10. **InvestmentPortfolio** - Investment tracking

## 🔐 API Endpoints

### Authentication (`/api/admin/auth`)

```
POST   /register              # Register new admin
POST   /login                 # Admin login
POST   /refresh               # Refresh JWT token
GET    /me                    # Get admin profile
POST   /change-password       # Change password
```

### Clients (`/api/admin/clients`)

```
GET    /                      # List all clients (paginated)
GET    /<client_id>           # Get client details
PUT    /<client_id>           # Update client info (name, IBAN, balance, etc.)
POST   /<client_id>/suspend   # Suspend account
POST   /<client_id>/activate  # Activate account
```

### Operations (`/api/admin/operations`)

#### Dashboard
```
GET    /dashboard             # Overview statistics
```

#### Beneficiaries
```
GET    /<client_id>/beneficiaries          # List beneficiaries
POST   /<client_id>/beneficiaries          # Add beneficiary
PUT    /beneficiaries/<beneficiary_id>     # Update beneficiary
DELETE /beneficiaries/<beneficiary_id>     # Delete beneficiary
```

#### Savings Account
```
GET    /<client_id>/accounts/savings       # Get savings account
PUT    /<client_id>/accounts/savings       # Update savings balance
```

#### Crypto Wallet
```
GET    /<client_id>/accounts/crypto        # Get crypto holdings
PUT    /<client_id>/accounts/crypto        # Update crypto balances
```

#### Investment Portfolio
```
GET    /<client_id>/accounts/investment    # Get investments
PUT    /<client_id>/accounts/investment    # Update portfolio
```

### Credits (`/api/admin/credits`)

```
GET    /                             # List all credit requests
GET    /<credit_id>                  # Get credit with schedule
POST   /<client_id>/request          # Create new credit request
PUT    /<credit_id>                  # Update credit details
POST   /<credit_id>/approve          # Approve credit
POST   /<credit_id>/reject           # Reject credit
```

### Transactions (`/api/admin/transactions`)

```
GET    /                             # List transactions (filterable)
GET    /<transaction_id>             # Get transaction details
PUT    /<transaction_id>             # Modify transaction (amount, recipient)
POST   /<transaction_id>/block       # Block transaction
POST   /<transaction_id>/unblock     # Unblock transaction
POST   /<transaction_id>/execute     # Execute transaction
POST   /<transaction_id>/cancel      # Cancel transaction
POST   /                             # Create new transaction
```

### Validation Codes (`/api/admin/codes`)

```
GET    /                             # List all codes
POST   /generate                     # Generate new code
POST   /<code_id>/verify             # Verify code
DELETE /<code_id>                    # Delete code
```

## 🔄 Key Features

### ✅ Real-time Client Management
- Modify name, phone, IBAN, BIC/Swift
- Update available balance instantly
- Manage KYC and account status

### ✅ Transaction Control
- **Modify amounts** before execution
- **Block/Unblock** without deletion
- Support for multiple types: SEPA, Instant, Crypto, Investments
- Full audit trail

### ✅ Credit Management
- **Automatic repayment schedule** calculation
- Monthly payment computation with interest
- Full installment tracking
- Approval/rejection workflows

### ✅ Beneficiary Management
- Add/Edit/Delete beneficiaries
- Verify IBAN/BIC codes
- SEPA transfer support

### ✅ Specialized Accounts
- **Savings**: Goals with progress tracking
- **Crypto**: BTC, ETH, USDT balances
- **Investments**: Portfolio tracking with ROI

### ✅ Security
- JWT authentication
- Role-based access control (admin, moderator, viewer)
- Validation code generation (6-digit, 15-min expiration)
- Attempt limiting on code verification

## 📊 Example Requests

### Login
```bash
curl -X POST http://localhost:5000/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@bitwise.com", "password": "password"}'
```

### Update Client Balance
```bash
curl -X PUT http://localhost:5000/api/admin/clients/client-id \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"available_balance": 5000.00}'
```

### Block Transaction
```bash
curl -X POST http://localhost:5000/api/admin/transactions/tx-id/block \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Suspicious activity detected"}'
```

### Generate Validation Code
```bash
curl -X POST http://localhost:5000/api/admin/codes/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code_type": "email", "recipient": "user@example.com", "expiration_minutes": 15}'
```

## 🛠️ Configuration

Edit `.env` file for:
- Database URL (PostgreSQL or SQLite)
- JWT secret key
- Flask environment (development/production)
- SMTP settings for emails

## 📝 License

Private - Bitwise Bank

## 👤 Support

For issues or questions, contact: dgiokrousi244@gmail.com
