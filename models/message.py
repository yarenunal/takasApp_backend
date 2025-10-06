from extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - backref çakışmasını önlemek için
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages_ref')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages_ref')
    trade = db.relationship('Trade', backref='messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'trade_id': self.trade_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver': self.receiver.to_dict() if self.receiver else None
        }
