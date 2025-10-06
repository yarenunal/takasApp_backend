from extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # 'main' veya 'sub'
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    icon = db.Column(db.String(100), nullable=True)  # Emoji veya icon
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referencing relationship for subcategories
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'is_active': self.is_active,
            'subcategories': [sub.to_dict() for sub in self.subcategories] if self.subcategories else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_main_categories(cls):
        """Ana kategorileri getir (Satış, Takas)"""
        return cls.query.filter_by(type='main', parent_id=None).all()
    
    @classmethod
    def get_subcategories_by_parent(cls, parent_id):
        """Belirli ana kategoriye ait alt kategorileri getir"""
        return cls.query.filter_by(parent_id=parent_id, type='sub').all()
    
    @classmethod
    def get_category_tree(cls):
        """Tüm kategori ağacını getir"""
        main_categories = cls.get_main_categories()
        return [cat.to_dict() for cat in main_categories]
