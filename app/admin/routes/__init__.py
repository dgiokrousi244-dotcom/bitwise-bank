from app.admin.routes.auth import auth_bp
from app.admin.routes.clients import clients_bp
from app.admin.routes.operations import operations_bp
from app.admin.routes.credits import credits_bp
from app.admin.routes.transactions import transactions_bp
from app.admin.routes.codes import codes_bp

__all__ = ['auth_bp', 'clients_bp', 'operations_bp', 'credits_bp', 'transactions_bp', 'codes_bp']
