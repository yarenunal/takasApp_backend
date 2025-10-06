from extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'items'  # Mevcut tablo adı
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(db.String(50), nullable=True, default='İyi')  # Az Kullanılmış, Yeni, vs.
    sale_type = db.Column(db.String(50), nullable=True, default='Satış')  # Satış, Takas, Her İkisi
    price = db.Column(db.Numeric(10, 2), nullable=True)
    price_range = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # Ana görsel URL'i
    status = db.Column(db.String(50), nullable=True, default='Aktif')  # Aktif, Pasif, Satıldı
    view_count = db.Column(db.Integer, default=0)  # Görüntülenme sayısı
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    owner = db.relationship('User', backref='products')
    category = db.relationship('Category', backref='products')
    # images relationship kaldırıldı - artık image_url sütunu kullanılıyor
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'condition': self.condition,
            'sale_type': self.sale_type,
            'price': float(self.price) if self.price else None,
            'price_range': self.price_range,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'location': self.location,
            'image_url': self.image_url,
            'status': self.status,
            'view_count': self.view_count,  # Görüntülenme sayısı
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': self.owner.to_dict() if self.owner else None,
            'category': self.category.to_dict() if self.category else None,
            # images kaldırıldı - artık image_url sütunu kullanılıyor
        }
    
    @classmethod
    def get_by_category(cls, category_id, page=1, per_page=20):
        """Kategoriye göre ürünleri getir"""
        return cls.query.filter_by(
            category_id=category_id,
            status='Aktif'
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def search_products(cls, search_term, page=1, per_page=20):
        """Ürün arama"""
        return cls.query.filter(
            db.or_(
                cls.title.contains(search_term),
                cls.description.contains(search_term)
            ),
            cls.status == 'Aktif'
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def get_by_user(cls, user_id, page=1, per_page=20):
        """Kullanıcının ürünlerini getir"""
        return cls.query.filter_by(
            user_id=user_id,
            status='Aktif'
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def get_active_products(cls, page=1, per_page=20):
        """Aktif ürünleri getir"""
        return cls.query.filter_by(
            status='Aktif'
        ).order_by(cls.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    def increment_view_count(self):
        """Ürün görüntülenme sayısını artır"""
        self.view_count += 1
        db.session.commit()
        return self.view_count
    
    def get_view_count_display(self):
        """Görüntülenme sayısını kullanıcı dostu formatta döndür"""
        if self.view_count < 1000:
            return f"{self.view_count} görüntülenme"
        elif self.view_count < 1000000:
            return f"{(self.view_count / 1000):.1f}K görüntülenme"
        else:
            return f"{(self.view_count / 1000000):.1f}M görüntülenme"
    
    def add_unique_view(self, viewer_user_id):
        """Benzersiz kullanıcı görüntülemesi ekle"""
        from models.product_view import ProductView
        
        # Daha önce bu kullanıcı tarafından görüntülenmiş mi?
        existing_view = ProductView.query.filter_by(
            product_id=self.id,
            viewer_user_id=viewer_user_id
        ).first()
        
        if not existing_view:
            # Yeni benzersiz görüntüleme
            new_view = ProductView(
                product_id=self.id,
                viewer_user_id=viewer_user_id
            )
            db.session.add(new_view)
            
            # Görüntülenme sayısını güncelle
            self.view_count = ProductView.query.filter_by(product_id=self.id).count()
            
            db.session.commit()
            logger.info(f"Benzersiz görüntüleme eklendi: Product {self.id}, User {viewer_user_id}, Total: {self.view_count}")
            return True
        else:
            logger.info(f"Tekrar görüntüleme: Product {self.id}, User {viewer_user_id} (sayı artmadı)")
            return False
    

