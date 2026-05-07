from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Client, Beneficiary, SavingsAccount, SavingsGoal, CryptoWallet, InvestmentPortfolio, Investment
from datetime import datetime

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get admin dashboard overview"""
    total_clients = Client.query.count()
    active_clients = Client.query.filter_by(account_status='active').count()
    total_balance = db.session.query(db.func.sum(Client.available_balance)).scalar() or 0
    
    return jsonify({
        'total_clients': total_clients,
        'active_clients': active_clients,
        'total_balance': total_balance,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Beneficiary operations
@operations_bp.route('/<client_id>/beneficiaries', methods=['GET'])
@jwt_required()
def get_beneficiaries(client_id):
    """Get client beneficiaries"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    beneficiaries = [{
        'id': b.id,
        'name': b.name,
        'iban': b.iban,
        'bic_swift': b.bic_swift,
        'account_type': b.account_type,
        'is_verified': b.is_verified,
        'created_at': b.created_at.isoformat()
    } for b in client.beneficiaries]
    
    return jsonify({'beneficiaries': beneficiaries}), 200

@operations_bp.route('/<client_id>/beneficiaries', methods=['POST'])
@jwt_required()
def add_beneficiary(client_id):
    """Add new beneficiary"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('iban'):
        return jsonify({'error': 'Missing name or IBAN'}), 400
    
    beneficiary = Beneficiary(
        client_id=client_id,
        name=data['name'],
        iban=data['iban'],
        bic_swift=data.get('bic_swift', ''),
        account_type=data.get('account_type', 'personal')
    )
    
    db.session.add(beneficiary)
    db.session.commit()
    
    return jsonify({
        'message': 'Beneficiary added successfully',
        'beneficiary_id': beneficiary.id
    }), 201

@operations_bp.route('/beneficiaries/<beneficiary_id>', methods=['PUT'])
@jwt_required()
def update_beneficiary(beneficiary_id):
    """Update beneficiary"""
    beneficiary = Beneficiary.query.get(beneficiary_id)
    
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        beneficiary.name = data['name']
    if 'iban' in data:
        beneficiary.iban = data['iban']
    if 'bic_swift' in data:
        beneficiary.bic_swift = data['bic_swift']
    if 'is_verified' in data:
        beneficiary.is_verified = data['is_verified']
    
    beneficiary.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Beneficiary updated successfully'}), 200

@operations_bp.route('/beneficiaries/<beneficiary_id>', methods=['DELETE'])
@jwt_required()
def delete_beneficiary(beneficiary_id):
    """Delete beneficiary"""
    beneficiary = Beneficiary.query.get(beneficiary_id)
    
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    db.session.delete(beneficiary)
    db.session.commit()
    
    return jsonify({'message': 'Beneficiary deleted successfully'}), 200

# Savings operations
@operations_bp.route('/<client_id>/accounts/savings', methods=['GET'])
@jwt_required()
def get_savings_account(client_id):
    """Get savings account"""
    savings = SavingsAccount.query.filter_by(client_id=client_id).first()
    
    if not savings:
        return jsonify({'error': 'Savings account not found'}), 404
    
    goals = [{
        'id': g.id,
        'name': g.name,
        'target_amount': g.target_amount,
        'current_amount': g.current_amount,
        'progress': (g.current_amount / g.target_amount * 100) if g.target_amount > 0 else 0,
        'deadline': g.deadline.isoformat() if g.deadline else None,
        'status': g.status
    } for g in savings.goals]
    
    return jsonify({
        'id': savings.id,
        'balance': savings.balance,
        'interest_rate': savings.interest_rate,
        'total_saved': savings.total_saved,
        'goals': goals
    }), 200

@operations_bp.route('/<client_id>/accounts/savings', methods=['PUT'])
@jwt_required()
def update_savings_account(client_id):
    """Update savings account"""
    savings = SavingsAccount.query.filter_by(client_id=client_id).first()
    
    if not savings:
        savings = SavingsAccount(client_id=client_id)
        db.session.add(savings)
        db.session.flush()
    
    data = request.get_json()
    
    if 'balance' in data:
        savings.balance = data['balance']
    if 'interest_rate' in data:
        savings.interest_rate = data['interest_rate']
    
    savings.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Savings account updated'}), 200

# Crypto operations
@operations_bp.route('/<client_id>/accounts/crypto', methods=['GET'])
@jwt_required()
def get_crypto_wallet(client_id):
    """Get crypto wallet"""
    crypto = CryptoWallet.query.filter_by(client_id=client_id).first()
    
    if not crypto:
        return jsonify({'error': 'Crypto wallet not found'}), 404
    
    return jsonify({
        'id': crypto.id,
        'bitcoin_balance': crypto.bitcoin_balance,
        'ethereum_balance': crypto.ethereum_balance,
        'usdt_balance': crypto.usdt_balance,
        'total_value_usd': crypto.total_value_usd
    }), 200

@operations_bp.route('/<client_id>/accounts/crypto', methods=['PUT'])
@jwt_required()
def update_crypto_wallet(client_id):
    """Update crypto wallet"""
    crypto = CryptoWallet.query.filter_by(client_id=client_id).first()
    
    if not crypto:
        crypto = CryptoWallet(client_id=client_id)
        db.session.add(crypto)
        db.session.flush()
    
    data = request.get_json()
    
    if 'bitcoin_balance' in data:
        crypto.bitcoin_balance = data['bitcoin_balance']
    if 'ethereum_balance' in data:
        crypto.ethereum_balance = data['ethereum_balance']
    if 'usdt_balance' in data:
        crypto.usdt_balance = data['usdt_balance']
    if 'total_value_usd' in data:
        crypto.total_value_usd = data['total_value_usd']
    
    crypto.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Crypto wallet updated'}), 200

# Investment operations
@operations_bp.route('/<client_id>/accounts/investment', methods=['GET'])
@jwt_required()
def get_investment_portfolio(client_id):
    """Get investment portfolio"""
    portfolio = InvestmentPortfolio.query.filter_by(client_id=client_id).first()
    
    if not portfolio:
        return jsonify({'error': 'Investment portfolio not found'}), 404
    
    investments = [{
        'id': i.id,
        'name': i.name,
        'type': i.type,
        'amount_invested': i.amount_invested,
        'current_value': i.current_value,
        'profit_loss': i.profit_loss,
        'purchase_date': i.purchase_date.isoformat()
    } for i in portfolio.investments]
    
    return jsonify({
        'id': portfolio.id,
        'total_invested': portfolio.total_invested,
        'current_value': portfolio.current_value,
        'total_profit_loss': portfolio.total_profit_loss,
        'roi_percentage': portfolio.roi_percentage,
        'investments': investments
    }), 200

@operations_bp.route('/<client_id>/accounts/investment', methods=['PUT'])
@jwt_required()
def update_investment_portfolio(client_id):
    """Update investment portfolio"""
    portfolio = InvestmentPortfolio.query.filter_by(client_id=client_id).first()
    
    if not portfolio:
        portfolio = InvestmentPortfolio(client_id=client_id)
        db.session.add(portfolio)
        db.session.flush()
    
    data = request.get_json()
    
    if 'total_invested' in data:
        portfolio.total_invested = data['total_invested']
    if 'current_value' in data:
        portfolio.current_value = data['current_value']
    if 'total_profit_loss' in data:
        portfolio.total_profit_loss = data['total_profit_loss']
    if 'roi_percentage' in data:
        portfolio.roi_percentage = data['roi_percentage']
    
    portfolio.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Investment portfolio updated'}), 200
