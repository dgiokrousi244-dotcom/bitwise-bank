from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Client, SavingsAccount, CryptoWallet, InvestmentPortfolio
from datetime import datetime

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('', methods=['GET'])
@jwt_required()
def get_all_clients():
    """Get all clients with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Client.query
    
    if search:
        query = query.filter(
            (Client.full_name.ilike(f'%{search}%')) |
            (Client.email.ilike(f'%{search}%')) |
            (Client.iban.ilike(f'%{search}%'))
        )
    
    pagination = query.order_by(Client.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    clients = [{
        'id': client.id,
        'full_name': client.full_name,
        'email': client.email,
        'phone': client.phone,
        'iban': client.iban,
        'bic_swift': client.bic_swift,
        'available_balance': client.available_balance,
        'kyc_status': client.kyc_status,
        'account_status': client.account_status,
        'created_at': client.created_at.isoformat()
    } for client in pagination.items]
    
    return jsonify({
        'clients': clients,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@clients_bp.route('/<client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    """Get client details"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    return jsonify({
        'id': client.id,
        'full_name': client.full_name,
        'email': client.email,
        'phone': client.phone,
        'iban': client.iban,
        'bic_swift': client.bic_swift,
        'available_balance': client.available_balance,
        'kyc_status': client.kyc_status,
        'account_status': client.account_status,
        'created_at': client.created_at.isoformat(),
        'updated_at': client.updated_at.isoformat()
    }), 200

@clients_bp.route('/<client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    """Update client information"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        client.full_name = data['full_name']
    if 'phone' in data:
        client.phone = data['phone']
    if 'iban' in data:
        client.iban = data['iban']
    if 'bic_swift' in data:
        client.bic_swift = data['bic_swift']
    if 'available_balance' in data:
        client.available_balance = data['available_balance']
    if 'kyc_status' in data:
        client.kyc_status = data['kyc_status']
    if 'account_status' in data:
        client.account_status = data['account_status']
    
    client.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Client updated successfully'}), 200

@clients_bp.route('/<client_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_client(client_id):
    """Suspend client account"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    client.account_status = 'suspended'
    client.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Client account suspended'}), 200

@clients_bp.route('/<client_id>/activate', methods=['POST'])
@jwt_required()
def activate_client(client_id):
    """Activate client account"""
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    client.account_status = 'active'
    client.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Client account activated'}), 200
