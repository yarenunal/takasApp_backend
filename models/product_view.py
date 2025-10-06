from extensions import db
from datetime import datetime

class ProductView(db.Model):
    __tablename__ = 'product_views'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    viewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    product = db.relationship('Product', backref='views')
    viewer = db.relationship('User', backref='viewed_products')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'viewer_user_id': self.viewer_user_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'viewer_name': self.viewer.first_name if self.viewer else None
        }
    
    def __repr__(self):
        return f'<ProductView {self.id}: User {self.viewer_user_id} -> Product {self.product_id}>'
    
    @classmethod
    def get_unique_viewers_count(cls, product_id):
        """Bir ürünün kaç farklı kullanıcı tarafından görüntülendiğini getir"""
        return cls.query.filter_by(product_id=product_id).count()
    
    @classmethod
    def has_user_viewed_product(cls, product_id, user_id):
        """Kullanıcı bu ürünü daha önce görüntülemiş mi?"""
        return cls.query.filter_by(
            product_id=product_id,
            viewer_user_id=user_id
        ).first() is not None
