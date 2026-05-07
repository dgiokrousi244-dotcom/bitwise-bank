from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import CreditRequest, RepaymentSchedule, Client
from datetime import datetime, timedelta

credits_bp = Blueprint('credits', __name__)

def calculate_repayment_schedule(amount, duration_months, annual_rate):
    """Calculate monthly repayment schedule"""
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        monthly_payment = amount / duration_months
    else:
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** duration_months) / \
                        ((1 + monthly_rate) ** duration_months - 1)
    
    schedule = []
    remaining_balance = amount
    current_date = datetime.utcnow()
    
    for i in range(1, duration_months + 1):
        interest = remaining_balance * monthly_rate
        principal = monthly_payment - interest
        remaining_balance -= principal
        
        due_date = current_date + timedelta(days=30*i)
        
        schedule.append({
            'installment_number': i,
            'due_date': due_date.date().isoformat(),
            'amount': round(monthly_payment, 2),
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'remaining_balance': round(max(0, remaining_balance), 2)
        })
    
    return round(monthly_payment, 2), schedule

@credits_bp.route('', methods=['GET'])
@jwt_required()
def get_all_credit_requests():
    """Get all credit requests with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = CreditRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    pagination = query.order_by(CreditRequest.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    credits = [{
        'id': credit.id,
        'client_id': credit.client_id,
        'client_name': credit.client.full_name,
        'amount_requested': credit.amount_requested,
        'amount_approved': credit.amount_approved,
        'duration_months': credit.duration_months,
        'interest_rate': credit.interest_rate,
        'status': credit.status,
        'monthly_payment': credit.monthly_payment,
        'created_at': credit.created_at.isoformat()
    } for credit in pagination.items]
    
    return jsonify({
        'credits': credits,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@credits_bp.route('/<credit_id>', methods=['GET'])
@jwt_required()
def get_credit_request(credit_id):
    """Get credit request with full repayment schedule"""
    credit = CreditRequest.query.get(credit_id)
    
    if not credit:
        return jsonify({'error': 'Credit request not found'}), 404
    
    schedule = [{
        'id': item.id,
        'installment_number': item.installment_number,
        'due_date': item.due_date.isoformat(),
        'amount': item.amount,
        'principal': item.principal,
        'interest': item.interest,
        'paid_amount': item.paid_amount,
        'payment_status': item.payment_status,
        'paid_date': item.paid_date.isoformat() if item.paid_date else None
    } for item in credit.repayment_schedule]
    
    return jsonify({
        'id': credit.id,
        'client_id': credit.client_id,
        'client_name': credit.client.full_name,
        'amount_requested': credit.amount_requested,
        'amount_approved': credit.amount_approved,
        'duration_months': credit.duration_months,
        'interest_rate': credit.interest_rate,
        'status': credit.status,
        'purpose': credit.purpose,
        'monthly_payment': credit.monthly_payment,
        'repayment_schedule': schedule,
        'created_at': credit.created_at.isoformat(),
        'updated_at': credit.updated_at.isoformat()
    }), 200

@credits_bp.route('/<client_id>/request', methods=['POST'])
@jwt_required()
def create_credit_request(client_id):
    """Create a new credit request"""
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('amount_requested') or not data.get('duration_months'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    amount = data['amount_requested']
    duration = data['duration_months']
    interest_rate = data.get('interest_rate', 5.0)  # Default 5% annual
    purpose = data.get('purpose', 'General')
    
    # Calculate monthly payment and schedule
    monthly_payment, schedule = calculate_repayment_schedule(amount, duration, interest_rate)
    
    credit = CreditRequest(
        client_id=client_id,
        amount_requested=amount,
        duration_months=duration,
        interest_rate=interest_rate,
        status='pending',
        purpose=purpose,
        monthly_payment=monthly_payment
    )
    
    db.session.add(credit)
    db.session.flush()
    
    # Create repayment schedule
    for item in schedule:
        repayment = RepaymentSchedule(
            credit_id=credit.id,
            installment_number=item['installment_number'],
            due_date=datetime.fromisoformat(item['due_date']).date(),
            amount=item['amount'],
            principal=item['principal'],
            interest=item['interest']
        )
        db.session.add(repayment)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Credit request created successfully',
        'credit_id': credit.id,
        'monthly_payment': monthly_payment
    }), 201

@credits_bp.route('/<credit_id>', methods=['PUT'])
@jwt_required()
def update_credit_request(credit_id):
    """Update credit request"""
    credit = CreditRequest.query.get(credit_id)
    
    if not credit:
        return jsonify({'error': 'Credit request not found'}), 404
    
    data = request.get_json()
    
    if 'amount_requested' in data:
        credit.amount_requested = data['amount_requested']
    if 'duration_months' in data:
        credit.duration_months = data['duration_months']
    if 'interest_rate' in data:
        credit.interest_rate = data['interest_rate']
    if 'purpose' in data:
        credit.purpose = data['purpose']
    
    credit.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Credit request updated successfully'}), 200

@credits_bp.route('/<credit_id>/approve', methods=['POST'])
@jwt_required()
def approve_credit(credit_id):
    """Approve a credit request"""
    credit = CreditRequest.query.get(credit_id)
    
    if not credit:
        return jsonify({'error': 'Credit request not found'}), 404
    
    data = request.get_json()
    approved_amount = data.get('approved_amount', credit.amount_requested)
    
    credit.status = 'approved'
    credit.amount_approved = approved_amount
    credit.updated_at = datetime.utcnow()
    
    # Update client balance
    credit.client.available_balance += approved_amount
    
    db.session.commit()
    
    return jsonify({
        'message': 'Credit request approved',
        'credit_id': credit.id,
        'amount_approved': approved_amount
    }), 200

@credits_bp.route('/<credit_id>/reject', methods=['POST'])
@jwt_required()
def reject_credit(credit_id):
    """Reject a credit request"""
    credit = CreditRequest.query.get(credit_id)
    
    if not credit:
        return jsonify({'error': 'Credit request not found'}), 404
    
    credit.status = 'rejected'
    credit.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Credit request rejected'}), 200
