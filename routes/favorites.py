from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.favorite import Favorite
from models.product import Product
from extensions import db
from utils.logger import logger

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_favorites():
    """Ürünü favorilere ekle"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        product_id = data.get('product_id')
        
        print(f"🔍 DEBUG: Favori ekleme isteği: User {user_id}, Product {product_id}")
        logger.info(f"Favori ekleme isteği: User {user_id}, Product {product_id}")
        
        if not product_id:
            return jsonify({'error': 'product_id gerekli'}), 400
            
        # Debug: Tüm ürünleri listele
        all_products = Product.query.all()
        print(f"🔍 DEBUG: Tüm ürünler: {[p.id for p in all_products]}")
        
        # Debug: Doğrudan SQL ile kontrol et
        from sqlalchemy import text
        result = db.session.execute(text("SELECT id FROM items WHERE id = :id"), {"id": product_id})
        sql_product = result.fetchone()
        print(f"🔍 DEBUG: SQL query sonucu: {sql_product}")
        
        # Debug: Product model'inde tablo adını kontrol et
        print(f"🔍 DEBUG: Product.__tablename__: {Product.__tablename__}")
        print(f"🔍 DEBUG: Product.__table__.name: {Product.__table__.name}")
        
        # SQL sonucu ile ürün var mı kontrol et
        if not sql_product:
            return jsonify({'error': 'Ürün bulunamadı (SQL)'}), 404
            
        # Ürün var mı kontrol et (ORM ile)
        product = Product.query.get(product_id)
        print(f"🔍 DEBUG: Product query sonucu: {product}")
        logger.info(f"Product query sonucu: {product}")
        
        if not product:
            print(f"⚠️ DEBUG: ORM ile ürün bulunamadı ama SQL ile var!")
            # ORM çalışmıyorsa SQL ile devam et
            pass
        else:
            print(f"✅ DEBUG: ORM ile ürün bulundu!")
            
        # Zaten favori mi kontrol et
        existing = Favorite.query.filter_by(
            user_id=user_id, 
            product_id=product_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Ürün zaten favorilerde'}), 400
            
        # Favorilere ekle
        favorite = Favorite(user_id=user_id, product_id=product_id)
        db.session.add(favorite)
        db.session.commit()
        
        logger.info(f"Ürün favorilere eklendi: User {user_id}, Product {product_id}")
        
        return jsonify({
            'message': 'Ürün favorilere eklendi',
            'favorite': favorite.to_dict()
        }), 201
        
    except Exception as e:
        print(f"💥 DEBUG: Favori ekleme hatası: {str(e)}")
        logger.error(f"Favori ekleme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori eklenemedi'}), 500

@favorites_bp.route('/', methods=['GET'])
@jwt_required()
def get_favorites():
    """Kullanıcının favori ürünlerini getir"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        favorites = Favorite.query.filter_by(user_id=user_id)\
            .join(Product)\
            .order_by(Favorite.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        products = []
        for favorite in favorites.items:
            product_data = favorite.product.to_dict()
            product_data['favorited_at'] = favorite.created_at.isoformat()
            products.append(product_data)
            
        return jsonify({
            'products': products,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': favorites.total,
                'pages': favorites.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Favori ürünleri getirme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori ürünleri getirilemedi'}), 500

@favorites_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_favorites(product_id):
    """Ürünü favorilerden çıkar"""
    try:
        user_id = int(get_jwt_identity())
        
        favorite = Favorite.query.filter_by(
            user_id=user_id, 
            product_id=product_id
        ).first()
        
        if not favorite:
            return jsonify({'error': 'Favori bulunamadı'}), 404
            
        db.session.delete(favorite)
        db.session.commit()
        
        logger.info(f"Ürün favorilerden çıkarıldı: User {user_id}, Product {product_id}")
        
        return jsonify({'message': 'Ürün favorilerden çıkarıldı'}), 200
        
    except Exception as e:
        logger.error(f"Favori çıkarma hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori çıkarılamadı'}), 500

@favorites_bp.route('/<int:product_id>/check', methods=['GET'])
@jwt_required()
def check_favorite(product_id):
    """Ürünün favori olup olmadığını kontrol et"""
    try:
        user_id = int(get_jwt_identity())
        
        favorite = Favorite.query.filter_by(
            user_id=user_id, 
            product_id=product_id
        ).first()
        
        return jsonify({
            'is_favorite': favorite is not None,
            'favorited_at': favorite.created_at.isoformat() if favorite else None
        }), 200
        
    except Exception as e:
        logger.error(f"Favori kontrol hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori kontrol edilemedi'}), 500
