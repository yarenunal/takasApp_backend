from flask import Blueprint, request, jsonify
from extensions import db
from models.category import Category
from utils.logger import logger
from flask_jwt_extended import jwt_required, get_jwt_identity

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['GET'])
def get_categories():
    """Tüm kategorileri getir"""
    try:
        categories = Category.get_category_tree()
        logger.info("Kategoriler başarıyla getirildi")
        return jsonify({
            'message': 'Kategoriler başarıyla getirildi',
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Kategoriler getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Kategoriler getirilemedi'}), 500

@category_bp.route('/main', methods=['GET'])
def get_main_categories():
    """Ana kategorileri getir (Satış, Takas)"""
    try:
        main_categories = Category.get_main_categories()
        categories = [cat.to_dict() for cat in main_categories]
        logger.info("Ana kategoriler başarıyla getirildi")
        return jsonify({
            'message': 'Ana kategoriler başarıyla getirildi',
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Ana kategoriler getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Ana kategoriler getirilemedi'}), 500

@category_bp.route('/<int:category_id>/subcategories', methods=['GET'])
def get_subcategories(category_id):
    """Belirli ana kategoriye ait alt kategorileri getir"""
    try:
        subcategories = Category.get_subcategories_by_parent(category_id)
        categories = [cat.to_dict() for cat in subcategories]
        logger.info(f"Alt kategoriler başarıyla getirildi: {category_id}")
        return jsonify({
            'message': 'Alt kategoriler başarıyla getirildi',
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Alt kategoriler getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Alt kategoriler getirilemedi'}), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Belirli kategoriyi getir"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Kategori bulunamadı'}), 404
        
        logger.info(f"Kategori başarıyla getirildi: {category_id}")
        return jsonify({
            'message': 'Kategori başarıyla getirildi',
            'category': category.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Kategori getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Kategori getirilemedi'}), 500

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """Yeni kategori oluştur (Admin için)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['name', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} gerekli'}), 400
        
        # Kategori türünü kontrol et
        if data['type'] not in ['main', 'sub']:
            return jsonify({'error': 'Kategori türü main veya sub olmalı'}), 400
        
        # Alt kategori için parent_id gerekli
        if data['type'] == 'sub' and not data.get('parent_id'):
            return jsonify({'error': 'Alt kategori için parent_id gerekli'}), 400
        
        category = Category(
            name=data['name'],
            description=data.get('description'),
            type=data['type'],
            parent_id=data.get('parent_id'),
            icon=data.get('icon')
        )
        
        db.session.add(category)
        db.session.commit()
        
        logger.info(f"Kategori başarıyla oluşturuldu: {category.name} - ID: {category.id}")
        logger.log_user_action(current_user_id, 'category_created', {'name': category.name, 'type': category.type})
        
        return jsonify({
            'message': 'Kategori başarıyla oluşturuldu',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Kategori oluşturulamadı: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Kategori oluşturulamadı'}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Kategori güncelle (Admin için)"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Kategori bulunamadı'}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            category.name = data['name']
        if data.get('description') is not None:
            category.description = data['description']
        if data.get('icon') is not None:
            category.icon = data['icon']
        if data.get('is_active') is not None:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f"Kategori başarıyla güncellendi: {category.name} - ID: {category.id}")
        logger.log_user_action(current_user_id, 'category_updated', {'name': category.name, 'id': category.id})
        
        return jsonify({
            'message': 'Kategori başarıyla güncellendi',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Kategori güncellenemedi: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Kategori güncellenemedi'}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Kategori sil (Admin için)"""
    try:
        current_user_id = get_jwt_identity()
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Kategori bulunamadı'}), 404
        
        # Alt kategorileri varsa silme
        if category.subcategories:
            return jsonify({'error': 'Alt kategorileri olan kategori silinemez'}), 400
        
        # Ürünleri varsa silme
        if hasattr(category, 'products') and category.products:
            return jsonify({'error': 'Ürünleri olan kategori silinemez'}), 400
        
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        logger.info(f"Kategori başarıyla silindi: {category_name} - ID: {category_id}")
        logger.log_user_action(current_user_id, 'category_deleted', {'name': category_name, 'id': category_id})
        
        return jsonify({'message': 'Kategori başarıyla silindi'}), 200
        
    except Exception as e:
        logger.error(f"Kategori silinemedi: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Kategori silinemedi'}), 500
