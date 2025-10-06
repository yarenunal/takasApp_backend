from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Import all route modules
from .auth import auth_bp
from .otp import otp_bp
from .products import products_bp
from .category import category_bp
from .trades import trades_bp
from .messages import messages_bp
from .favorites import favorites_bp
from .complaints import complaints_bp

# Register route blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(otp_bp, url_prefix='/otp')
api_bp.register_blueprint(products_bp, url_prefix='/products')
api_bp.register_blueprint(category_bp, url_prefix='/categories')
api_bp.register_blueprint(trades_bp, url_prefix='/trades')
api_bp.register_blueprint(messages_bp, url_prefix='/messages')
api_bp.register_blueprint(favorites_bp, url_prefix='/favorites')
api_bp.register_blueprint(complaints_bp, url_prefix='/complaints')
