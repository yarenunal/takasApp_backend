from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.trade import Trade
from models.product import Product

trades_bp = Blueprint('trades', __name__)

@trades_bp.route('/', methods=['GET'])
@jwt_required()
def get_trades():
    """Get user's trades"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    trades = Trade.query.filter_by(user_id=current_user_id).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'trades': [trade.to_dict() for trade in trades.items],
        'total': trades.total,
        'pages': trades.pages,
        'current_page': page
    }), 200

@trades_bp.route('/', methods=['POST'])
@jwt_required()
def create_trade():
    """Create new trade offer"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('product_id'):
        return jsonify({'error': 'Product ID is required'}), 400
    
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product.owner_id == current_user_id:
        return jsonify({'error': 'Cannot trade your own product'}), 400
    
    if product.status != 'available':
        return jsonify({'error': 'Product is not available for trade'}), 400
    
    try:
        trade = Trade(
            product_id=data['product_id'],
            user_id=current_user_id,
            message=data.get('message', '')
        )
        
        db.session.add(trade)
        db.session.commit()
        
        return jsonify({
            'message': 'Trade offer created successfully',
            'trade': trade.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Trade creation failed'}), 500

@trades_bp.route('/<int:trade_id>/status', methods=['PUT'])
@jwt_required()
def update_trade_status(trade_id):
    """Update trade status (accept/reject)"""
    current_user_id = get_jwt_identity()
    trade = Trade.query.get(trade_id)
    
    if not trade:
        return jsonify({'error': 'Trade not found'}), 404
    
    # Only product owner can update trade status
    if trade.product.owner_id != current_user_id:
        return jsonify({'error': 'Can only update trades for own products'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        trade.status = new_status
        
        if new_status == 'accepted':
            trade.product.status = 'traded'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Trade {new_status} successfully',
            'trade': trade.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Status update failed'}), 500
