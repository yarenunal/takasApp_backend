from extensions import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Mevcut alan
    first_name = db.Column(db.String(100), nullable=True)  # Yeni alan
    last_name = db.Column(db.String(100), nullable=True)  # Yeni alan
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    avatar_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # Yeni alan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender_user')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver_user')
    user_trades = db.relationship('Trade', backref='trade_user')  # user_trades olarak değiştirdim
    
    def __init__(self, name, phone, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.phone = phone
        if 'email' in kwargs:
            self.email = kwargs['email']
        if 'location' in kwargs:
            self.location = kwargs['location']
    
    def set_password(self, password):
        """Şifre hashleme (gelecekte kullanım için)"""
        if hasattr(self, 'password_hash'):
            self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Şifre kontrolü (gelecekte kullanım için)"""
        if hasattr(self, 'password_hash'):
            return bcrypt.check_password_hash(self.password_hash, password)
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,
            'location': self.location,
            'rating': self.rating,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_phone(cls, phone):
        """Telefon numarası ile kullanıcı bul"""
        return cls.query.filter_by(phone=phone).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Email ile kullanıcı bul"""
        if email:
            return cls.query.filter_by(email=email).first()
        return None
