from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.message import Message
from models.user import User

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/', methods=['GET'])
@jwt_required()
def get_messages():
    """Get user's messages"""
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get messages where user is sender or receiver
    messages = Message.query.filter(
        (Message.sender_id == current_user_id) | 
        (Message.receiver_id == current_user_id)
    ).order_by(Message.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'messages': [message.to_dict() for message in messages.items],
        'total': messages.total,
        'pages': messages.pages,
        'current_page': page
    }), 200

@messages_bp.route('/', methods=['POST'])
@jwt_required()
def send_message():
    """Send a new message"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('receiver_id') or not data.get('content'):
        return jsonify({'error': 'Receiver ID and content are required'}), 400
    
    # Check if receiver exists
    receiver = User.query.get(data['receiver_id'])
    if not receiver:
        return jsonify({'error': 'Receiver not found'}), 404
    
    try:
        message = Message(
            sender_id=current_user_id,
            receiver_id=data['receiver_id'],
            trade_id=data.get('trade_id'),
            content=data['content']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_data': message.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Message sending failed'}), 500

@messages_bp.route('/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(message_id):
    """Mark message as read"""
    current_user_id = get_jwt_identity()
    message = Message.query.get(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Only receiver can mark message as read
    if message.receiver_id != current_user_id:
        return jsonify({'error': 'Can only mark own messages as read'}), 403
    
    try:
        message.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Message marked as read',
            'message_data': message.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Update failed'}), 500
