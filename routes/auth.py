from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.otp import OTP
from utils.logger import logger
import random
import string

auth_bp = Blueprint('auth', __name__)

def generate_random_otp(length=6):
    """Random OTP kodu üret"""
    return ''.join(random.choices(string.digits, k=length))

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Access token'ı yenile"""
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Token yenileme isteği: User {current_user_id}")
        
        # Yeni access token oluştur
        new_access_token = create_access_token(identity=str(current_user_id))
        
        logger.info(f"Token yenilendi: User {current_user_id}")
        
        return jsonify({
            'message': 'Token başarıyla yenilendi',
            'access_token': new_access_token,
            'user_id': current_user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Token yenileme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token yenilenemedi'}), 500

@auth_bp.route('/send-otp', methods=['POST'])
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

@auth_bp.route('/register', methods=['POST'])
def register():
    logger.info("User registration attempt")
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Registration failed: Missing field '{field}'")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            logger.warning(f"Registration failed: Username '{data['username']}' already exists")
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Registration failed: Email '{data['email']}' already exists")
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")
        logger.log_user_action(user.id, 'register', {'username': user.username, 'email': user.email})
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Registration failed with exception: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500



@auth_bp.route('/login', methods=['POST'])
def login():
    """Telefon numarası ile giriş"""
    logger.info("Kullanıcı girişi denemesi")
    
    try:
        data = request.get_json()
        
        if not data.get('phone'):
            logger.warning("Giriş başarısız: Telefon numarası eksik")
            return jsonify({'error': 'Telefon numarası gerekli'}), 400
        
        phone = data['phone']
        
        # Telefon numarası formatını kontrol et
        if not phone.startswith('+90') and not phone.startswith('0'):
            phone = '+90' + phone.lstrip('0')
        
        # Kullanıcıyı bul
        user = User.get_by_phone(phone)
        
        if not user:
            logger.warning(f"Giriş başarısız: Kullanıcı bulunamadı: {phone}")
            return jsonify({'error': 'Bu telefon numarası ile kayıtlı kullanıcı bulunamadı'}), 401
        
        # Kullanıcı aktif mi kontrol et
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"Giriş başarısız: Pasif hesap: {phone}")
            return jsonify({'error': 'Hesap pasif durumda'}), 401
        
        # JWT token oluştururken sub field'ını string'e çevir
        access_token = create_access_token(identity=str(user.id))  # str() ekle
        refresh_token = create_refresh_token(identity=str(user.id))  # str() ekle
        
        logger.info(f"Kullanıcı başarıyla giriş yaptı: {user.name} - {phone}")
        logger.log_user_action(user.id, 'login', {'ip': request.remote_addr, 'phone': phone})
        
        return jsonify({
            'message': 'Giriş başarılı',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Giriş başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'Giriş başarısız'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """OTP doğrula ve kullanıcı oluştur"""
    logger.info("OTP doğrulama denemesi")
    
    try:
        data = request.get_json()
        
        if not data.get('phone') or not data.get('otp'):
            logger.warning("OTP doğrulama başarısız: Eksik veri")
            return jsonify({'error': 'Telefon ve OTP gerekli'}), 400
        
        phone = data['phone']
        otp = data['otp']
        
        # Telefon numarası formatını kontrol et
        if not phone.startswith('+90') and not phone.startswith('0'):
            phone = '+90' + phone.lstrip('0')
        
        # OTP doğrulama (mock - gerçek uygulamada OTP modeli kullanılır)
        # Test için herhangi bir 6 haneli OTP kabul edilir
        if len(otp) == 6 and otp.isdigit():
            # Kullanıcıyı bul veya oluştur
            user = User.get_by_phone(phone)
            
            if not user:
                # Yeni kullanıcı oluştur
                user = User(
                    phone=phone,
                    name=f"Kullanıcı {phone[-4:]}"
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"Yeni kullanıcı oluşturuldu: {phone}")
            
            # JWT token oluştur
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            logger.info(f"OTP doğrulama başarılı: {phone}")
            logger.log_user_action(user.id, 'otp_verified', {'ip': request.remote_addr, 'phone': phone})
            
            return jsonify({
                'message': 'OTP doğrulandı',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200
        else:
            logger.warning(f"OTP doğrulama başarısız: Yanlış OTP - {phone}")
            return jsonify({'error': 'Geçersiz OTP'}), 400
            
    except Exception as e:
        logger.error(f"OTP doğrulama hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'OTP doğrulanamadı'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Kullanıcı profili"""
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Profil isteği - Kullanıcı ID: {current_user_id}")
        
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"Profil isteği başarısız: Kullanıcı bulunamadı - ID: {current_user_id}")
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        logger.log_user_action(user.id, 'profile_view')
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Profil isteği başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'Profil isteği başarısız'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Profil güncelleme"""
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Profil güncelleme denemesi - Kullanıcı ID: {current_user_id}")
        
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"Profil güncelleme başarısız: Kullanıcı bulunamadı - ID: {current_user_id}")
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Güncellenebilir alanlar
        updatable_fields = ['name', 'email', 'location', 'avatar_url']
        updated_fields = []
        
        for field in updatable_fields:
            if field in data:
                old_value = getattr(user, field)
                setattr(user, field, data[field])
                updated_fields.append(f"{field}: {old_value} -> {data[field]}")
        
        if updated_fields:
            try:
                db.session.commit()
                logger.info(f"Profil başarıyla güncellendi: {user.name} - ID: {current_user_id}")
                logger.log_user_action(user.id, 'profile_update', {'updated_fields': updated_fields})
                
                return jsonify({
                    'message': 'Profil başarıyla güncellendi',
                    'user': user.to_dict()
                }), 200
            except Exception as e:
                logger.error(f"Veritabanı commit başarısız: {str(e)}", exc_info=True)
                db.session.rollback()
                return jsonify({'error': 'Güncelleme başarısız'}), 500
        else:
            logger.info(f"Güncellenecek alan yok - Kullanıcı ID: {current_user_id}")
            return jsonify({'message': 'Değişiklik yapılmadı'}), 200
            
    except Exception as e:
        logger.error(f"Profil güncelleme başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'Güncelleme başarısız'}), 500

@auth_bp.route('/profile/create', methods=['POST'])
@jwt_required()
def create_profile():
    """Profil oluşturma"""
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Profil oluşturma denemesi - Kullanıcı ID: {current_user_id}")
        
        # Debug: Authorization header'ı kontrol et
        auth_header = request.headers.get('Authorization')
        logger.info(f"Authorization header: {auth_header}")
        
        # Debug: Gelen veriyi logla
        data = request.get_json()
        logger.info(f"Gelen veri: {data}")
        
        user = User.query.get(current_user_id)
        
        if not user:
            logger.warning(f"Profil oluşturma başarısız: Kullanıcı bulunamadı - ID: {current_user_id}")
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Zorunlu alanlar kontrolü
        required_fields = ['first_name', 'last_name', 'location']
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"Profil oluşturma başarısız: Eksik alanlar: {missing_fields}")
            return jsonify({
                'error': f'Eksik alanlar: {", ".join(missing_fields)}',
                'missing_fields': missing_fields
            }), 400
        
        # Debug: Mevcut kullanıcı bilgilerini logla
        logger.info(f"Mevcut kullanıcı: {user.to_dict()}")
        
        # Profil bilgilerini güncelle
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.location = data['location']
        
        # Opsiyonel alanlar
        if data.get('avatar_url'):
            user.avatar_url = data['avatar_url']
        
        # Debug: Güncellenecek bilgileri logla
        logger.info(f"Güncellenecek bilgiler: first_name={data['first_name']}, last_name={data['last_name']}, location={data['location']}")
        
        try:
            db.session.commit()
            logger.info(f"Profil başarıyla oluşturuldu: {user.first_name} {user.last_name} - ID: {current_user_id}")
            logger.log_user_action(user.id, 'profile_created', {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'location': user.location
            })
            
            # Debug: Güncellenmiş kullanıcı bilgilerini logla
            updated_user = user.to_dict()
            logger.info(f"Güncellenmiş kullanıcı: {updated_user}")
            
            return jsonify({
                'message': 'Profil başarıyla oluşturuldu',
                'user': updated_user,
                'redirect': 'dashboard',
                'success': True,
                'status': 'completed',
                'next_step': 'redirect_to_dashboard',
                'user_id': user.id,
                'profile_complete': True
            }), 200
            
        except Exception as e:
            logger.error(f"Veritabanı commit başarısız: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'error': 'Veritabanı hatası: ' + str(e)}), 500
        
    except Exception as e:
        logger.error(f"Profil oluşturma başarısız: {str(e)}", exc_info=True)
        return jsonify({'error': 'Profil oluşturma hatası: ' + str(e)}), 500

@auth_bp.route('/test-token', methods=['GET'])
def test_token():
    """JWT token test endpoint'i - test için token olmadan da çalışır"""
    try:
        # Test için sabit bir kullanıcı ID kullan
        test_user_id = 1
        logger.info(f"Test token - Kullanıcı ID: {test_user_id}")
        
        user = User.query.get(test_user_id)
        if not user:
            return jsonify({'error': 'Test kullanıcısı bulunamadı'}), 404
        
        # Test için JWT token oluştur
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=str(test_user_id))
        
        return jsonify({
            'message': 'Test token oluşturuldu',
            'access_token': access_token,
            'user_id': test_user_id,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Test token hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Test token hatası: ' + str(e)}), 500

@auth_bp.route('/debug-token', methods=['POST'])
def debug_token():
    """JWT token debug endpoint'i - token olmadan da çalışır"""
    try:
        # Authorization header'ı kontrol et
        auth_header = request.headers.get('Authorization')
        logger.info(f"Debug - Authorization header: {auth_header}")
        
        if not auth_header:
            return jsonify({
                'error': 'Authorization header eksik',
                'note': 'Header formatı: Authorization: Bearer <token>'
            }), 401
        
        # Bearer prefix kontrolü
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Yanlış Authorization formatı',
                'current': auth_header,
                'expected': 'Bearer <token>',
                'note': 'Bearer prefix eksik'
            }), 401
        
        # Token'ı ayır
        token = auth_header.replace('Bearer ', '')
        logger.info(f"Debug - Token: {token[:20]}... (ilk 20 karakter)")
        
        # Token segment sayısını kontrol et
        segments = token.split('.')
        logger.info(f"Debug - Token segment sayısı: {len(segments)}")
        
        if len(segments) != 3:
            return jsonify({
                'error': 'JWT token formatı yanlış',
                'segments': len(segments),
                'expected': 3,
                'note': 'JWT token 3 segment olmalı: header.payload.signature'
            }), 400
        
        return jsonify({
            'message': 'Token formatı doğru',
            'segments': len(segments),
            'header_length': len(segments[0]),
            'payload_length': len(segments[1]),
            'signature_length': len(segments[2])
        }), 200
        
    except Exception as e:
        logger.error(f"Token debug hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token debug hatası: ' + str(e)}), 500
