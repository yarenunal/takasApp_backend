from extensions import db
from datetime import datetime

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    reason = db.Column(db.String(500), nullable=False)  # Şikayet nedeni
    description = db.Column(db.Text, nullable=True)     # Detaylı açıklama
    status = db.Column(db.String(50), default='pending')  # pending, reviewed, resolved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref='complaints')
    product = db.relationship('Product', backref='complaints')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'product_title': self.product.title if self.product else None,
            'product_image': self.product.image_url if self.product else None
        }
    
    def __repr__(self):
        return f'<Complaint {self.id}: User {self.user_id} -> Product {self.product_id}>'
