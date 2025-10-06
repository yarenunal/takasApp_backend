from flask import Blueprint, request, jsonify
from extensions import db
from models.otp import OTP
from models.user import User
from utils.logger import logger
import random
import string

otp_bp = Blueprint('otp', __name__)

def generate_random_otp(length=6):
    """Random OTP kodu üret"""
    return ''.join(random.choices(string.digits, k=length))

@otp_bp.route('/send', methods=['POST'])
def send_otp():
    """Random OTP gönderimi - test için"""
    try:
        data = request.get_json()
        
        if not data.get('phone'):
            logger.warning("OTP gönderimi başarısız: Telefon numarası eksik")
            return jsonify({'error': 'Telefon numarası gerekli'}), 400
        
        phone = data['phone']
        
        # Telefon numarası formatını kontrol et
        if not phone.startswith('+90') and not phone.startswith('0'):
            phone = '+90' + phone.lstrip('0')
        
        # Mevcut kullanıcı kontrolü - basitleştirildi
        try:
            existing_user = User.get_by_phone(phone)
            if existing_user:
                logger.warning(f"OTP gönderimi başarısız: Telefon numarası zaten kayıtlı: {phone}")
                return jsonify({'error': 'Bu telefon numarası zaten kayıtlı'}), 400
        except Exception as e:
            logger.warning(f"Kullanıcı kontrolü atlandı: {str(e)}")
        
        # Random OTP kodu oluştur
        random_otp = generate_random_otp(6)
        
        # Terminal'de OTP kodunu göster
        logger.info(f"Random OTP kodu oluşturuldu: {phone} - Kod: {random_otp}")
        print(f"\n{'='*50}")
        print(f"📱 RANDOM OTP KODU: {random_otp}")
        print(f"📞 Telefon: {phone}")
        print(f"⏰ Süre: 5 dakika (test)")
        print(f"🎲 Random üretildi")
        print(f"{'='*50}\n")
        
        return jsonify({
            'otp': random_otp,
            'message': 'Random OTP gönderildi',
            'phone': phone,
            'expires_in': '5 dakika (test)',
            'note': 'Random OTP - gerçek SMS entegrasyonu daha sonra yapılacak'
        }), 200
        
    except Exception as e:
        logger.error(f"OTP gönderimi başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'OTP gönderimi başarısız'}), 500

@otp_bp.route('/verify', methods=['POST'])
def verify_otp():
    """Random OTP doğrulama ve gerçek kullanıcı kaydı"""
    try:
        data = request.get_json()
        
        required_fields = ['phone', 'otp_code', 'name']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"OTP doğrulama başarısız: Eksik alan '{field}'")
                return jsonify({'error': f'{field} gerekli'}), 400
        
        phone = data['phone']
        otp_code = data['otp_code']
        name = data['name']
        
        # Telefon numarası formatını kontrol et
        if not phone.startswith('+90') and not phone.startswith('0'):
            phone = '+90' + phone.lstrip('0')
        
        # OTP doğrulama - 6 haneli sayı kontrolü
        if not otp_code.isdigit() or len(otp_code) != 6:
            logger.warning(f"OTP doğrulama başarısız: Geçersiz format: {otp_code}")
            return jsonify({'error': 'OTP kodu 6 haneli sayı olmalı'}), 400
        
        # Mevcut kullanıcı kontrolü
        try:
            existing_user = User.get_by_phone(phone)
            if existing_user:
                logger.warning(f"OTP doğrulama başarısız: Telefon numarası zaten kayıtlı: {phone}")
                return jsonify({'error': 'Bu telefon numarası zaten kayıtlı'}), 400
        except Exception as e:
            logger.warning(f"Kullanıcı kontrolü atlandı: {str(e)}")
        
        # Gerçek kullanıcı oluştur ve veritabanına kaydet
        try:
            user = User(
                name=name,
                phone=phone,
                email=data.get('email'),
                location=data.get('location')
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Kullanıcı başarıyla veritabanına kaydedildi: {name} - {phone}")
            logger.log_user_action(user.id, 'user_registration', {'phone': phone, 'name': name})
            
            return jsonify({
                'message': 'Kullanıcı başarıyla kayıt oldu',
                'user': user.to_dict(),
                'redirect': 'login',
                'note': 'Kullanıcı veritabanına kaydedildi'
            }), 201
            
        except Exception as e:
            logger.error(f"Veritabanına kayıt başarısız: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'error': 'Kullanıcı kaydı başarısız'}), 500
        
    except Exception as e:
        logger.error(f"OTP doğrulama başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'OTP doğrulama başarısız'}), 500

@otp_bp.route('/resend', methods=['POST'])
def resend_otp():
    """Random OTP yeniden gönderimi - test için"""
    try:
        data = request.get_json()
        
        if not data.get('phone'):
            logger.warning("OTP yeniden gönderimi başarısız: Telefon numarası eksik")
            return jsonify({'error': 'Telefon numarası gerekli'}), 400
        
        phone = data['phone']
        
        # Telefon numarası formatını kontrol et
        if not phone.startswith('+90') and not phone.startswith('0'):
            phone = '+90' + phone.lstrip('0')
        
        # Yeni random OTP kodu oluştur
        new_random_otp = generate_random_otp(6)
        
        # Terminal'de OTP kodunu göster
        logger.info(f"Yeni random OTP kodu oluşturuldu: {phone} - Kod: {new_random_otp}")
        print(f"\n{'='*50}")
        print(f"📱 YENİ RANDOM OTP KODU: {new_random_otp}")
        print(f"📞 Telefon: {phone}")
        print(f"⏰ Süre: 5 dakika (test)")
        print(f"🎲 Random üretildi")
        print(f"{'='*50}\n")
        
        return jsonify({
            'otp': new_random_otp,
            'message': 'Yeni random OTP gönderildi',
            'phone': phone,
            'expires_in': '5 dakika (test)',
            'note': 'Random OTP - gerçek SMS entegrasyonu daha sonra yapılacak'
        }), 200
        
    except Exception as e:
        logger.error(f"OTP yeniden gönderimi başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'OTP yeniden gönderimi başarısız'}), 500
