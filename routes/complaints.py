from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.complaint import Complaint
from models.product import Product
from utils.logger import logger

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/', methods=['POST'])
@jwt_required()
def create_complaint():
    """Yeni şikayet oluştur"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Debug: Gelen veriyi logla
        logger.info(f"Şikayet verisi: {data}")
        logger.info(f"Current user ID: {current_user_id}")
        
        # Gerekli alanları kontrol et
        required_fields = ['product_id', 'reason']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Eksik alan: {field}")
                return jsonify({'error': f'{field} gerekli'}), 400
        
        product_id = data['product_id']
        reason = data['reason']
        description = data.get('description', '')
        
        # Ürün var mı kontrol et
        product = Product.query.get(product_id)
        if not product:
            logger.error(f"Ürün bulunamadı: {product_id}")
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        logger.info(f"Ürün bulundu: {product.title}, Owner: {product.user_id}")
        
        # Kullanıcı kendi ürününe şikayet edemez
        if product.user_id == current_user_id:
            logger.error(f"Kendi ürününe şikayet: User {current_user_id}, Product {product_id}")
            return jsonify({'error': 'Kendi ürününüze şikayet edemezsiniz'}), 400
        
        # Daha önce şikayet edilmiş mi kontrol et
        existing_complaint = Complaint.query.filter_by(
            user_id=current_user_id,
            product_id=product_id
        ).first()
        
        if existing_complaint:
            logger.error(f"Duplicate şikayet: User {current_user_id}, Product {product_id}, Complaint ID: {existing_complaint.id}")
            return jsonify({'error': 'Bu ürün için zaten şikayet oluşturdunuz'}), 400
        
        # Şikayet oluştur
        complaint = Complaint(
            user_id=current_user_id,
            product_id=product_id,
            reason=reason,
            description=description
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        logger.info(f"Şikayet oluşturuldu: User {current_user_id}, Product {product_id}")
        logger.log_user_action(current_user_id, 'complaint_created', {
            'product_id': product_id,
            'reason': reason
        })
        
        return jsonify({
            'message': 'Şikayet başarıyla oluşturuldu',
            'complaint': complaint.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Şikayet oluşturma hatası: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Şikayet oluşturulamadı'}), 500

@complaints_bp.route('/my-complaints', methods=['GET'])
@jwt_required()
def get_my_complaints():
    """Kullanıcının şikayetlerini getir"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Kullanıcının şikayetlerini getir
        complaints = Complaint.query.filter_by(user_id=current_user_id).order_by(Complaint.created_at.desc()).all()
        
        logger.info(f"Kullanıcı şikayetleri getirildi: User {current_user_id}, Toplam: {len(complaints)}")
        
        return jsonify({
            'message': 'Şikayetler başarıyla getirildi',
            'complaints': [complaint.to_dict() for complaint in complaints],
            'total': len(complaints)
        }), 200
        
    except Exception as e:
        logger.error(f"Şikayet getirme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Şikayetler getirilemedi'}), 500

@complaints_bp.route('/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    """Belirli şikayeti getir"""
    try:
        current_user_id = int(get_jwt_identity())
        
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({'error': 'Şikayet bulunamadı'}), 404
        
        # Sadece şikayet sahibi görebilir
        if complaint.user_id != current_user_id:
            return jsonify({'error': 'Bu şikayeti görme yetkiniz yok'}), 403
        
        return jsonify({
            'message': 'Şikayet başarıyla getirildi',
            'complaint': complaint.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Şikayet getirme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Şikayet getirilemedi'}), 500

@complaints_bp.route('/<int:complaint_id>', methods=['DELETE'])
@jwt_required()
def delete_complaint(complaint_id):
    """Şikayeti sil"""
    try:
        current_user_id = int(get_jwt_identity())
        
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({'error': 'Şikayet bulunamadı'}), 404
        
        # Sadece şikayet sahibi silebilir
        if complaint.user_id != current_user_id:
            return jsonify({'error': 'Bu şikayeti silme yetkiniz yok'}), 403
        
        db.session.delete(complaint)
        db.session.commit()
        
        logger.info(f"Şikayet silindi: User {current_user_id}, Complaint {complaint_id}")
        
        return jsonify({
            'message': 'Şikayet başarıyla silindi'
        }), 200
        
    except Exception as e:
        logger.error(f"Şikayet silme hatası: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Şikayet silinemedi'}), 500
