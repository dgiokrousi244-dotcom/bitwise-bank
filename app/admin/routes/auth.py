from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Admin
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new admin"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    admin = Admin(
        email=data['email'],
        full_name=data.get('full_name', ''),
        role=data.get('role', 'admin')
    )
    admin.set_password(data['password'])
    
    db.session.add(admin)
    db.session.commit()
    
    return jsonify({'message': 'Admin registered successfully', 'admin_id': admin.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login admin"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    admin = Admin.query.filter_by(email=data['email']).first()
    
    if not admin or not admin.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not admin.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    access_token = create_access_token(identity=admin.id)
    refresh_token = create_refresh_token(identity=admin.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'admin_id': admin.id,
        'email': admin.email,
        'full_name': admin.full_name
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    admin_id = get_jwt_identity()
    access_token = create_access_token(identity=admin_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Get admin profile"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    return jsonify({
        'id': admin.id,
        'email': admin.email,
        'full_name': admin.full_name,
        'role': admin.role,
        'is_active': admin.is_active,
        'created_at': admin.created_at.isoformat()
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change admin password"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing old or new password'}), 400
    
    if not admin.check_password(data['old_password']):
        return jsonify({'error': 'Old password is incorrect'}), 401
    
    admin.set_password(data['new_password'])
    admin.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200
