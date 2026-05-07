from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import ValidationCode
from datetime import datetime, timedelta
import random
import string

codes_bp = Blueprint('codes', __name__)

def generate_validation_code():
    """Generate a 6-digit validation code"""
    return ''.join(random.choices(string.digits, k=6))

@codes_bp.route('', methods=['GET'])
@jwt_required()
def get_all_codes():
    """Get all validation codes"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    type_filter = request.args.get('type', '', type=str)
    
    query = ValidationCode.query
    
    if type_filter:
        query = query.filter_by(code_type=type_filter)
    
    pagination = query.order_by(ValidationCode.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    codes = [{
        'id': code.id,
        'code': code.code,
        'code_type': code.code_type,
        'recipient': code.recipient,
        'is_used': code.is_used,
        'is_valid': code.is_valid,
        'attempts': code.attempts,
        'expires_at': code.expires_at.isoformat(),
        'created_at': code.created_at.isoformat()
    } for code in pagination.items]
    
    return jsonify({
        'codes': codes,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@codes_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_code():
    """Generate a new validation code"""
    data = request.get_json()
    
    if not data or not data.get('code_type') or not data.get('recipient'):
        return jsonify({'error': 'Missing code_type or recipient'}), 400
    
    code_value = generate_validation_code()
    
    # Check if code already exists
    while ValidationCode.query.filter_by(code=code_value).first():
        code_value = generate_validation_code()
    
    # Set expiration (default 15 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=data.get('expiration_minutes', 15))
    
    validation_code = ValidationCode(
        code=code_value,
        code_type=data['code_type'],
        recipient=data['recipient'],
        expires_at=expires_at,
        max_attempts=data.get('max_attempts', 3)
    )
    
    db.session.add(validation_code)
    db.session.commit()
    
    return jsonify({
        'message': 'Validation code generated',
        'code_id': validation_code.id,
        'code': validation_code.code,
        'expires_at': expires_at.isoformat()
    }), 201

@codes_bp.route('/<code_id>/verify', methods=['POST'])
@jwt_required()
def verify_code(code_id):
    """Verify a validation code"""
    validation_code = ValidationCode.query.get(code_id)
    
    if not validation_code:
        return jsonify({'error': 'Validation code not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('code'):
        return jsonify({'error': 'Missing code'}), 400
    
    if not validation_code.is_valid:
        return jsonify({'error': 'Code is invalid or expired'}), 400
    
    if validation_code.code != data['code']:
        validation_code.attempts += 1
        db.session.commit()
        return jsonify({
            'error': 'Incorrect code',
            'attempts_remaining': validation_code.max_attempts - validation_code.attempts
        }), 401
    
    validation_code.is_used = True
    validation_code.used_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Code verified successfully'}), 200

@codes_bp.route('/<code_id>', methods=['DELETE'])
@jwt_required()
def delete_code(code_id):
    """Delete a validation code"""
    validation_code = ValidationCode.query.get(code_id)
    
    if not validation_code:
        return jsonify({'error': 'Validation code not found'}), 404
    
    db.session.delete(validation_code)
    db.session.commit()
    
    return jsonify({'message': 'Validation code deleted'}), 200
