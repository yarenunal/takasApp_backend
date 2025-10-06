#!/usr/bin/env python3
"""
Takas Backend - Ürünlere sale_type Ekle
Mevcut ürünlere satış/takas/her ikisi bilgisi ekler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.product import Product
from extensions import db

def update_products_sale_type():
    """Mevcut ürünlere sale_type ekle"""
    
    with app.app_context():
        try:
            # Ürünleri güncelle
            products_to_update = [
                # Elektronik - Satış
                {'id': 4, 'sale_type': 'Satış', 'title': 'iPhone 12'},
                {'id': 5, 'sale_type': 'Satış', 'title': 'iPhone 13 Pro Max'},
                {'id': 6, 'sale_type': 'Satış', 'title': 'iPhone 13 Pro Max'},
                {'id': 7, 'sale_type': 'Takas', 'title': 'Test iPhone 12'},
                
                # Yeni eklenen ürünler - Çeşitli
                {'id': 8, 'sale_type': 'Her İkisi', 'title': 'iPhone 13 Pro'},
                {'id': 9, 'sale_type': 'Satış', 'title': 'MacBook Air M1'},
                {'id': 10, 'sale_type': 'Takas', 'title': 'Nike Air Max 270'},
                {'id': 11, 'sale_type': 'Her İkisi', 'title': 'Zara Kış Montu'},
                {'id': 12, 'sale_type': 'Her İkisi', 'title': 'iPhone 13 Pro (2)'},
                {'id': 13, 'sale_type': 'Satış', 'title': 'MacBook Air M1 (2)'},
                {'id': 14, 'sale_type': 'Takas', 'title': 'Nike Air Max 270 (2)'},
                {'id': 15, 'sale_type': 'Her İkisi', 'title': 'Zara Kış Montu (2)'},
                {'id': 16, 'sale_type': 'Satış', 'title': 'IKEA Malm Yatak Odası'},
                {'id': 17, 'sale_type': 'Takas', 'title': 'Philips Airfryer XXL'},
                {'id': 18, 'sale_type': 'Her İkisi', 'title': 'Trek Marlin 7 Bisiklet'},
                {'id': 19, 'sale_type': 'Takas', 'title': 'Adidas Predator Top'},
                {'id': 20, 'sale_type': 'Satış', 'title': 'Harry Potter Serisi'},
                {'id': 21, 'sale_type': 'Her İkisi', 'title': 'Yamaha PSR-E373 Klavye'},
            ]
            
            updated_count = 0
            
            for product_data in products_to_update:
                product = Product.query.get(product_data['id'])
                if product:
                    old_sale_type = product.sale_type
                    product.sale_type = product_data['sale_type']
                    db.session.add(product)
                    updated_count += 1
                    print(f"✅ {product_data['title']} güncellendi: {old_sale_type} → {product_data['sale_type']}")
                else:
                    print(f"⚠️ Ürün bulunamadı: ID {product_data['id']}")
            
            # Veritabanına kaydet
            db.session.commit()
            print(f"\n🎉 {updated_count} ürün başarıyla güncellendi!")
            
            # Güncellenmiş ürünleri listele
            print("\n📋 Güncellenmiş Ürünler:")
            print("=" * 50)
            products = Product.query.all()
            for product in products:
                print(f"ID {product.id}: {product.title} - {product.sale_type}")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("🔄 Takas Backend - Ürünlere sale_type Ekleme")
    print("=" * 50)
    update_products_sale_type()
