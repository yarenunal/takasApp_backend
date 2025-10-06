from flask import Blueprint, request, jsonify
from extensions import db
from models.product import Product
from models.favorite import Favorite
# from models.image import Image  # Image model kaldırıldı
from models.category import Category
from utils.logger import logger
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
import time

products_bp = Blueprint('products', __name__)

# Dosya upload ayarları
UPLOAD_FOLDER = 'uploads/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_product_image():
    """Ürün fotoğrafı yükle (Galeri)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Dosya kontrolü
        if 'image' not in request.files:
            return jsonify({'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if file and allowed_file(file.filename):
            # Güvenli dosya adı oluştur
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            unique_filename = f"{current_user_id}_{timestamp}_{filename}"
            
            # Upload klasörünü oluştur
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Dosyayı kaydet
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # URL oluştur
            image_url = f"/uploads/products/{unique_filename}"
            
            logger.info(f"Ürün fotoğrafı yüklendi: {image_url} - Kullanıcı: {current_user_id}")
            
            return jsonify({
                'message': 'Fotoğraf başarıyla yüklendi',
                'image_url': image_url,
                'filename': unique_filename
            }), 201
        
        return jsonify({'error': 'Geçersiz dosya türü'}), 400
        
    except Exception as e:
        logger.error(f"Fotoğraf yükleme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Fotoğraf yüklenemedi'}), 500

@products_bp.route('/upload-camera-image', methods=['POST'])
@jwt_required()
def upload_camera_image():
    """Kamera ile çekilen ürün fotoğrafını yükle"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Base64 image kontrolü
        if not data.get('image_data'):
            return jsonify({'error': 'Fotoğraf verisi bulunamadı'}), 400
        
        image_data = data['image_data']
        image_format = data.get('format', 'jpeg')  # jpeg, png, webp
        
        # Base64 prefix'i kaldır
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            logger.error(f"Base64 decode hatası: {str(e)}")
            return jsonify({'error': 'Geçersiz fotoğraf formatı'}), 400
        
        # Dosya adı oluştur
        timestamp = str(int(time.time()))
        unique_filename = f"{current_user_id}_{timestamp}_camera.{image_format}"
        
        # Upload klasörünü oluştur
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Dosyayı kaydet
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        # URL oluştur
        image_url = f"/uploads/products/{unique_filename}"
        
        logger.info(f"Kamera fotoğrafı yüklendi: {image_url} - Kullanıcı: {current_user_id}")
        
        return jsonify({
            'message': 'Kamera fotoğrafı başarıyla yüklendi',
            'image_url': image_url,
            'filename': unique_filename,
            'source': 'camera'
        }), 201
        
    except Exception as e:
        logger.error(f"Kamera fotoğrafı yükleme hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Kamera fotoğrafı yüklenemedi'}), 500

@products_bp.route('/', methods=['GET'])
def get_products():
    """Tüm aktif ürünleri getir"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        sale_type = request.args.get('sale_type', type=str)
        search = request.args.get('search', type=str)
        
        # Eski sağlam yapı korundu, sadece sale_type eklendi
        if category_id:
            # Kategori filtresi - eski mantık korundu
            products = Product.get_by_category(category_id, page, per_page)
            # Eğer sale_type da varsa, sonuçları filtrele
            if sale_type:
                # Frontend'den gelen sale_type değerlerini backend değerlerine eşle
                sale_type_mapping = {
                    'sale': 'Satış',
                    'exchange': 'Takas', 
                    'both': 'Her İkisi'
                }
                backend_sale_type = sale_type_mapping.get(sale_type, sale_type)
                products.items = [p for p in products.items if p.sale_type == backend_sale_type]
                products.total = len(products.items)
        elif search:
            products = Product.search_products(search, page, per_page)
        else:
            products = Product.get_active_products(page, per_page)
        
        logger.info(f"Ürünler başarıyla getirildi: sayfa {page}, toplam {products.total}")
        
        return jsonify({
            'message': 'Ürünler başarıyla getirildi',
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Ürünler getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Ürünler getirilemedi'}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Belirli ürünü getir"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        # JWT token'dan kullanıcı ID'sini al (eğer varsa)
        current_user_id = None
        try:
            from flask_jwt_extended import get_jwt_identity
            current_user_id = get_jwt_identity()
        except:
            # JWT token yoksa anonymous user olarak işaretle
            current_user_id = 0
        
        # Benzersiz kullanıcı görüntülemesi ekle
        if current_user_id:
            is_new_view = product.add_unique_view(current_user_id)
            if is_new_view:
                logger.info(f"Benzersiz görüntüleme: Product {product_id}, User {current_user_id}, Total: {product.view_count}")
            else:
                logger.info(f"Tekrar görüntüleme: Product {product_id}, User {current_user_id} (sayı artmadı)")
        else:
            # Anonymous user için basit artırma
            product.increment_view_count()
            logger.info(f"Anonymous görüntüleme: Product {product_id}, Total: {product.view_count}")
        
        logger.info(f"Ürün başarıyla getirildi: {product_id} - Benzersiz Görüntülenme: {product.view_count}")
        
        return jsonify({
            'message': 'Ürün başarıyla getirildi',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Ürün getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Ürün getirilemedi'}), 500



@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Yeni ürün oluştur"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['title', 'description', 'condition', 'sale_type', 'category_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} gerekli'}), 400
        
        # Kategori kontrolü
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Kategori bulunamadı'}), 404
        
        # Ürün oluştur
        product = Product(
            title=data['title'],
            description=data['description'],
            condition=data['condition'],
            sale_type=data['sale_type'],
            category_id=data['category_id'],
            user_id=current_user_id,
            price=data.get('price'),
            price_range=data.get('price_range'),
            location=data.get('location'),
            image_url=data.get('image_url')  # image_url eklendi
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Ürün başarıyla oluşturuldu: {product.title} - ID: {product.id}")
        logger.log_user_action(current_user_id, 'product_created', {'title': product.title, 'category_id': product.category_id})
        
        return jsonify({
            'message': 'Ürün başarıyla oluşturuldu',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Ürün oluşturulamadı: {str(e)}", exc_info=True)
        return jsonify({'error': 'Ürün oluşturulamadı'}), 500

@products_bp.route('/my-products/', methods=['GET'])
@jwt_required()
def get_my_products():
    """Kullanıcının kendi ürünlerini getir"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Kullanıcının ürünlerini getir
        products = Product.query.filter_by(user_id=current_user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logger.info(f"Kullanıcı ürünleri başarıyla getirildi: kullanıcı {current_user_id}, sayfa {page}")
        
        return jsonify({
            'message': 'Kullanıcı ürünleri başarıyla getirildi',
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Kullanıcı ürünleri getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Kullanıcı ürünleri getirilemedi'}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Ürün güncelle"""
    try:
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        # Sadece ürün sahibi güncelleyebilir
        if product.user_id != current_user_id:
            return jsonify({'error': 'Bu ürünü güncelleyemezsiniz'}), 403
        
        data = request.get_json()
        
        # Güncellenebilir alanlar
        updatable_fields = ['title', 'description', 'condition', 'sale_type', 'price', 'price_range', 'location', 'status']
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        
        logger.info(f"Ürün başarıyla güncellendi: {product.title} - ID: {product.id}")
        logger.log_user_action(current_user_id, 'product_updated', {'title': product.title, 'id': product.id})
        
        return jsonify({
            'message': 'Ürün başarıyla güncellendi',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Ürün güncellenemedi: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Ürün güncellenemedi'}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Ürün sil"""
    try:
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        # Sadece ürün sahibi silebilir
        if product.user_id != current_user_id:
            return jsonify({'error': 'Bu ürünü silemezsiniz'}), 403
        
        # Ürüne ait görselleri sil
        # Image.query.filter_by(item_id=product_id).delete() # Image model kaldırıldı
        
        product_title = product.title
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Ürün başarıyla silindi: {product_title} - ID: {product_id}")
        logger.log_user_action(current_user_id, 'product_deleted', {'title': product_title, 'id': product_id})
        
        return jsonify({'message': 'Ürün başarıyla silindi'}), 200
        
    except Exception as e:
        logger.error(f"Ürün silinemedi: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Ürün silinemedi'}), 500

@products_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_products(user_id):
    """Kullanıcının ürünlerini getir"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        products = Product.get_by_user(user_id, page, per_page)
        
        logger.info(f"Kullanıcı ürünleri başarıyla getirildi: {user_id}, sayfa {page}")
        
        return jsonify({
            'message': 'Kullanıcı ürünleri başarıyla getirildi',
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Kullanıcı ürünleri getirilemedi: {str(e)}", exc_info=True)
        return jsonify({'error': 'Kullanıcı ürünleri getirilemedi'}), 500

@products_bp.route('/<int:product_id>/images', methods=['POST'])
@jwt_required()
def add_product_image(product_id):
    """Ürüne görsel ekle"""
    try:
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        # Sadece ürün sahibi görsel ekleyebilir
        if product.user_id != current_user_id:
            return jsonify({'error': 'Bu ürüne görsel ekleyemezsiniz'}), 403
        
        data = request.get_json()
        if not data.get('image_url'):
            return jsonify({'error': 'Görsel URL gerekli'}), 400
        
        # Görsel ekle
        # image = Image( # Image model kaldırıldı
        #     item_id=product_id,
        #     image_url=data['image_url'],
        #     is_primary=data.get('is_primary', False)
        # )
        
        # İlk görsel ise primary yap
        # if not product.images.count(): # Image model kaldırıldı
        #     image.is_primary = True # Image model kaldırıldı
        
        # db.session.add(image) # Image model kaldırıldı
        db.session.commit()
        
        logger.info(f"Ürüne görsel eklendi: {product_id} - {data['image_url']}")
        logger.log_user_action(current_user_id, 'product_image_added', {'product_id': product_id, 'image_url': data['image_url']})
        
        return jsonify({
            'message': 'Görsel başarıyla eklendi',
            # 'image': image.to_dict() # Image model kaldırıldı
        }), 201
        
    except Exception as e:
        logger.error(f"Görsel eklenemedi: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Görsel eklenemedi'}), 500

@products_bp.route('/<int:product_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(product_id):
    """Ürünü favorilere ekle/çıkar"""
    try:
        print(f"🔍 DEBUG: Favori toggle başladı: Product {product_id}")
        current_user_id = int(get_jwt_identity())
        print(f"🔍 DEBUG: User ID: {current_user_id}")
        
        # Ürün var mı kontrol et
        product = Product.query.get(product_id)
        print(f"🔍 DEBUG: Product query sonucu: {product}")
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        print(f"🔍 DEBUG: Favorite model import edildi")
        
        # Zaten favori mi kontrol et
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user_id, 
            product_id=product_id
        ).first()
        print(f"🔍 DEBUG: Existing favorite: {existing_favorite}")
        
        if existing_favorite:
            # Favorilerden çıkar
            db.session.delete(existing_favorite)
            db.session.commit()
            
            print(f"🔍 DEBUG: Favori silindi")
            logger.info(f"Ürün favorilerden çıkarıldı: User {current_user_id}, Product {product_id}")
            
            return jsonify({
                'message': 'Ürün favorilerden çıkarıldı',
                'is_favorite': False
            }), 200
        else:
            # Favorilere ekle
            favorite = Favorite(user_id=current_user_id, product_id=product_id)
            print(f"🔍 DEBUG: Yeni favorite oluşturuldu: {favorite}")
            db.session.add(favorite)
            db.session.commit()
            
            print(f"🔍 DEBUG: Favori eklendi")
            logger.info(f"Ürün favorilere eklendi: User {current_user_id}, Product {product_id}")
            
            return jsonify({
                'message': 'Ürün favorilere eklendi',
                'is_favorite': True,
                'favorite': favorite.to_dict()
            }), 201
            
    except Exception as e:
        print(f"💥 DEBUG: Hata oluştu: {str(e)}")
        logger.error(f"Favori işlemi hatası: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Favori işlemi yapılamadı'}), 500

@products_bp.route('/<int:product_id>/favorite', methods=['GET'])
@jwt_required()
def check_favorite(product_id):
    """Ürünün favori olup olmadığını kontrol et"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Favori tablosunu import et
        # from models.favorite import Favorite # Bu satır zaten yukarıda import edilmiş
        
        # Favori var mı kontrol et
        favorite = Favorite.query.filter_by(
            user_id=current_user_id, 
            product_id=product_id
        ).first()
        
        is_favorite = favorite is not None
        
        return jsonify({
            'is_favorite': is_favorite,
            'product_id': product_id
        }), 200
        
    except Exception as e:
        logger.error(f"Favori kontrol hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori durumu kontrol edilemedi'}), 500

@products_bp.route('/<int:product_id>/favorite/status', methods=['GET'])
@jwt_required()
def get_favorite_status(product_id):
    """Ürünün favori durumunu getir (status endpoint)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Favori var mı kontrol et
        favorite = Favorite.query.filter_by(
            user_id=current_user_id, 
            product_id=product_id
        ).first()
        
        is_favorite = favorite is not None
        
        return jsonify({
            'is_favorite': is_favorite,
            'product_id': product_id,
            'status': 'favorited' if is_favorite else 'not_favorited'
        }), 200
        
    except Exception as e:
        logger.error(f"Favori status hatası: {str(e)}", exc_info=True)
        return jsonify({'error': 'Favori durumu getirilemedi'}), 500

@products_bp.route('/<int:product_id>/favorite', methods=['DELETE'])
@jwt_required()
def remove_favorite(product_id):
    """Ürünü favorilerden çıkar (DELETE method)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Ürün var mı kontrol et
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Ürün bulunamadı'}), 404
        
        # Favori var mı kontrol et
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user_id, 
            product_id=product_id
        ).first()
        
        if not existing_favorite:
            return jsonify({'error': 'Ürün zaten favorilerde değil'}), 400
        
        # Favoriyi sil
        db.session.delete(existing_favorite)
        db.session.commit()
        
        logger.info(f"Ürün favorilerden çıkarıldı: User {current_user_id}, Product {product_id}")
        
        return jsonify({
            'message': 'Ürün favorilerden çıkarıldı',
            'is_favorite': False,
            'product_id': product_id
        }), 200
        
    except Exception as e:
        logger.error(f"Favori çıkarma hatası: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Favori çıkarılamadı'}), 500
