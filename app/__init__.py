from flask import Flask
from flask_cors import CORS
from config import config
from app.extensions import db, jwt

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = 'development'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.admin.routes import auth_bp, clients_bp, operations_bp, credits_bp, transactions_bp, codes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/admin/auth')
    app.register_blueprint(clients_bp, url_prefix='/api/admin/clients')
    app.register_blueprint(operations_bp, url_prefix='/api/admin/operations')
    app.register_blueprint(credits_bp, url_prefix='/api/admin/credits')
    app.register_blueprint(transactions_bp, url_prefix='/api/admin/transactions')
    app.register_blueprint(codes_bp, url_prefix='/api/admin/codes')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
