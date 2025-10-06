from extensions import db
from datetime import datetime

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)  # items tablosuna referans
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, accepted, rejected, completed
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - backref çakışmasını önlemek için
    product = db.relationship('Product', backref='trades')
    user = db.relationship('User', backref='trade_user_ref')  # trade_user_ref olarak değiştirdim
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'product': self.product.to_dict() if self.product else None,
            'user': self.user.to_dict() if self.user else None
        }
