from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Transaction, Client
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_all_transactions():
    """Get all transactions with filters"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    type_filter = request.args.get('type', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    client_id = request.args.get('client_id', '', type=str)
    
    query = Transaction.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    pagination = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    transactions = [{
        'id': t.id,
        'client_id': t.client_id,
        'type': t.type,
        'amount': t.amount,
        'currency': t.currency,
        'status': t.status,
        'description': t.description,
        'recipient_name': t.recipient_name,
        'recipient_iban': t.recipient_iban,
        'blocked_reason': t.blocked_reason,
        'created_at': t.created_at.isoformat()
    } for t in pagination.items]
    
    return jsonify({
        'transactions': transactions,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Get transaction details"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({
        'id': transaction.id,
        'client_id': transaction.client_id,
        'type': transaction.type,
        'amount': transaction.amount,
        'currency': transaction.currency,
        'status': transaction.status,
        'description': transaction.description,
        'recipient_name': transaction.recipient_name,
        'recipient_iban': transaction.recipient_iban,
        'recipient_bic': transaction.recipient_bic,
        'blocked_reason': transaction.blocked_reason,
        'created_at': transaction.created_at.isoformat(),
        'executed_at': transaction.executed_at.isoformat() if transaction.executed_at else None
    }), 200

@transactions_bp.route('/<transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update transaction (modify amount, status)"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    # Allow modification only if pending
    if transaction.status != 'pending':
        return jsonify({'error': 'Can only modify pending transactions'}), 400
    
    if 'amount' in data:
        transaction.amount = data['amount']
    if 'description' in data:
        transaction.description = data['description']
    if 'recipient_name' in data:
        transaction.recipient_name = data['recipient_name']
    if 'recipient_iban' in data:
        transaction.recipient_iban = data['recipient_iban']
    if 'recipient_bic' in data:
        transaction.recipient_bic = data['recipient_bic']
    
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Transaction updated successfully'}), 200

@transactions_bp.route('/<transaction_id>/block', methods=['POST'])
@jwt_required()
def block_transaction(transaction_id):
    """Block a transaction"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    data = request.get_json() or {}
    reason = data.get('reason', 'Blocked by administrator')
    
    transaction.status = 'blocked'
    transaction.blocked_reason = reason
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Transaction blocked', 'reason': reason}), 200

@transactions_bp.route('/<transaction_id>/unblock', methods=['POST'])
@jwt_required()
def unblock_transaction(transaction_id):
    """Unblock a transaction"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if transaction.status != 'blocked':
        return jsonify({'error': 'Only blocked transactions can be unblocked'}), 400
    
    transaction.status = 'pending'
    transaction.blocked_reason = None
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Transaction unblocked'}), 200

@transactions_bp.route('/<transaction_id>/execute', methods=['POST'])
@jwt_required()
def execute_transaction(transaction_id):
    """Execute a transaction"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if transaction.status not in ['pending', 'blocked']:
        return jsonify({'error': 'Can only execute pending or blocked transactions'}), 400
    
    transaction.status = 'completed'
    transaction.executed_at = datetime.utcnow()
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Transaction executed successfully'}), 200

@transactions_bp.route('/<transaction_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_transaction(transaction_id):
    """Cancel a transaction"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if transaction.status in ['completed', 'cancelled']:
        return jsonify({'error': 'Cannot cancel completed or already cancelled transactions'}), 400
    
    transaction.status = 'cancelled'
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Transaction cancelled'}), 200

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    """Create a new transaction manually"""
    data = request.get_json()
    
    client = Client.query.get(data.get('client_id'))
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    transaction = Transaction(
        client_id=data['client_id'],
        type=data['type'],
        amount=data['amount'],
        currency=data.get('currency', 'EUR'),
        description=data.get('description', ''),
        recipient_name=data.get('recipient_name'),
        recipient_iban=data.get('recipient_iban'),
        recipient_bic=data.get('recipient_bic')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction_id': transaction.id
    }), 201
