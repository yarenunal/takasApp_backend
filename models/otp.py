from extensions import db
from datetime import datetime, timedelta
import random
import string

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, phone, expires_in_minutes=5):
        self.phone = phone
        self.otp_code = self._generate_otp()
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    
    def _generate_otp(self):
        """6 haneli OTP kodu oluştur"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """OTP süresi dolmuş mu?"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """OTP geçerli mi?"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """OTP'yi kullanıldı olarak işaretle"""
        self.is_used = True
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_latest_valid_otp(cls, phone):
        """Telefon numarası için en son geçerli OTP'yi getir"""
        return cls.query.filter_by(
            phone=phone,
            is_used=False
        ).filter(
            cls.expires_at > datetime.utcnow()
        ).order_by(cls.created_at.desc()).first()
    
    @classmethod
    def cleanup_expired_otps(cls):
        """Süresi dolmuş OTP'leri temizle"""
        expired_otps = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for otp in expired_otps:
            db.session.delete(otp)
        db.session.commit()
        return len(expired_otps)
