#!/usr/bin/env python3
"""
Takas Backend - Ürün Verilerini Ekle
10 farklı kategoride örnek ürünler ekler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.product import Product
from models.category import Category
from models.user import User
from extensions import db

def seed_products():
    """Örnek ürün verilerini ekle"""
    
    with app.app_context():
        try:
            # Kullanıcı kontrolü (test kullanıcısı)
            test_user = User.query.filter_by(phone='+90temp').first()
            if not test_user:
                print("❌ Test kullanıcısı bulunamadı. Önce OTP ile giriş yapın.")
                return
            
            # Kategori kontrolü
            categories = Category.query.all()
            if not categories:
                print("❌ Kategoriler bulunamadı. Önce kategorileri ekleyin.")
                return
            
            print(f"✅ {len(categories)} kategori bulundu")
            
            # Örnek ürün verileri
            sample_products = [
                # Elektronik
                {
                    'title': 'iPhone 13 Pro - Mükemmel Durumda',
                    'description': '256GB, Mavi, 1 yıl kullanıldı. Çizik yok, kutu dahil.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Her İkisi',
                    'price': 15000.00,
                    'price_range': '15000-16000',
                    'location': 'İstanbul',
                    'image_url': 'https://via.placeholder.com/400x300/007AFF/FFFFFF?text=iPhone+13+Pro',
                    'category_name': 'Elektronik'
                },
                {
                    'title': 'MacBook Air M1 - Yeni Gibi',
                    'description': '8GB RAM, 256GB SSD, 13 inç. 6 ay kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Satış',
                    'price': 25000.00,
                    'price_range': '25000-26000',
                    'location': 'Ankara',
                    'image_url': 'https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=MacBook+Air+M1',
                    'category_name': 'Elektronik'
                },
                
                # Giyim
                {
                    'title': 'Nike Air Max 270 - Erkek',
                    'description': '42 numara, siyah-beyaz. 3 ay kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Takas',
                    'price': None,
                    'price_range': None,
                    'location': 'İzmir',
                    'image_url': 'https://via.placeholder.com/400x300/00D4AA/FFFFFF?text=Nike+Air+Max',
                    'category_name': 'Giyim'
                },
                {
                    'title': 'Zara Kış Montu - Kadın',
                    'description': 'S numara, koyu mavi. 1 kış kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Her İkisi',
                    'price': 800.00,
                    'price_range': '800-900',
                    'location': 'Bursa',
                    'image_url': 'https://via.placeholder.com/400x300/6C5CE7/FFFFFF?text=Zara+Mont',
                    'category_name': 'Giyim'
                },
                
                # Mobilya
                {
                    'title': 'IKEA Malm Yatak Odası Takımı',
                    'description': '6 kapılı gardrop, komodin, yatak. 2 yıl kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Satış',
                    'price': 3000.00,
                    'price_range': '3000-3500',
                    'location': 'Antalya',
                    'image_url': 'https://via.placeholder.com/400x300/FDCB6E/FFFFFF?text=IKEA+Malm',
                    'category_name': 'Mobilya'
                },
                {
                    'title': 'Philips Airfryer XXL',
                    'description': '1.4L, dijital ekran. 1 yıl kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Takas',
                    'price': None,
                    'price_range': None,
                    'location': 'Eskişehir',
                    'image_url': 'https://via.placeholder.com/400x300/E17055/FFFFFF?text=Philips+Airfryer',
                    'category_name': 'Mobilya'
                },
                
                # Spor
                {
                    'title': 'Trek Marlin 7 MTB Bisiklet',
                    'description': '29 inç, 21 vites. 1 yıl kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Her İkisi',
                    'price': 8000.00,
                    'price_range': '8000-8500',
                    'location': 'Trabzon',
                    'image_url': 'https://via.placeholder.com/400x300/00B894/FFFFFF?text=Trek+Marlin+7',
                    'category_name': 'Spor'
                },
                {
                    'title': 'Adidas Predator Futbol Topu',
                    'description': '5 numara, profesyonel. 6 ay kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Takas',
                    'price': None,
                    'price_range': None,
                    'location': 'Konya',
                    'image_url': 'https://via.placeholder.com/400x300/FF7675/FFFFFF?text=Adidas+Predator',
                    'category_name': 'Spor'
                },
                
                # Kitap
                {
                    'title': 'Harry Potter Serisi - 7 Kitap',
                    'description': 'Türkçe, 1. baskı. Hafif yıpranmış.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Satış',
                    'price': 200.00,
                    'price_range': '200-250',
                    'location': 'Samsun',
                    'image_url': 'https://via.placeholder.com/400x300/74B9FF/FFFFFF?text=Harry+Potter',
                    'category_name': 'Kitap'
                },
                {
                    'title': 'Yamaha PSR-E373 Klavye',
                    'description': '61 tuş, 500 ses. 1 yıl kullanıldı.',
                    'condition': 'Az Kullanılmış',
                    'sale_type': 'Her İkisi',
                    'price': 2500.00,
                    'price_range': '2500-2700',
                    'location': 'Kayseri',
                    'image_url': 'https://via.placeholder.com/400x300/A29BFE/FFFFFF?text=Yamaha+Klavye',
                    'category_name': 'Kitap'
                }
            ]
            
            added_count = 0
            
            for product_data in sample_products:
                # Kategori bul
                category = Category.query.filter(
                    Category.name.contains(product_data['category_name'])
                ).first()
                
                if not category:
                    print(f"⚠️ Kategori bulunamadı: {product_data['category_name']}")
                    continue
                
                # Ürün oluştur
                product = Product(
                    title=product_data['title'],
                    description=product_data['description'],
                    condition=product_data['condition'],
                    sale_type=product_data['sale_type'],
                    price=product_data['price'],
                    price_range=product_data['price_range'],
                    location=product_data['location'],
                    image_url=product_data['image_url'],
                    category_id=category.id,
                    user_id=test_user.id
                )
                
                db.session.add(product)
                added_count += 1
                print(f"✅ {product_data['title']} eklendi")
            
            # Veritabanına kaydet
            db.session.commit()
            print(f"\n🎉 {added_count} ürün başarıyla eklendi!")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("🌱 Takas Backend - Ürün Verilerini Ekleme")
    print("=" * 50)
    seed_products()
