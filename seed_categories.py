#!/usr/bin/env python3
"""
Kategori seed script'i
Kategorileri veritabanına ekler
"""

from app import create_app
from extensions import db
from models.category import Category
from utils.logger import logger

def seed_categories():
    """Kategorileri veritabanına ekle"""
    app = create_app()
    
    with app.app_context():
        try:
            # Mevcut kategorileri kontrol et
            existing_categories = Category.query.all()
            logger.info(f"Mevcut kategoriler bulundu: {len(existing_categories)}")
            
            # Ana kategorileri oluştur veya güncelle
            satis = Category.query.filter_by(name="Satış").first()
            if not satis:
                satis = Category(
                    name="Satış",
                    description="Ürünlerin satışa sunulduğu kategori",
                    type="main",
                    icon="💰",
                    is_active=True
                )
                db.session.add(satis)
                db.session.commit()
                logger.info("Satış kategorisi oluşturuldu")
            else:
                satis.type = "main"
                satis.icon = "💰"
                satis.description = "Ürünlerin satışa sunulduğu kategori"
                db.session.commit()
                logger.info("Satış kategorisi güncellendi")
            
            takas = Category.query.filter_by(name="Takas").first()
            if not takas:
                takas = Category(
                    name="Takas",
                    description="Ürünlerin takas edildiği kategori",
                    type="main",
                    icon="🔄",
                    is_active=True
                )
                db.session.add(takas)
                db.session.commit()
                logger.info("Takas kategorisi oluşturuldu")
            else:
                takas.type = "main"
                takas.icon = "🔄"
                takas.description = "Ürünlerin takas edildiği kategori"
                db.session.commit()
                logger.info("Takas kategorisi güncellendi")
            
            # Mevcut kategorileri alt kategori yap
            alt_kategori_map = {
                "Elektronik": "📱",
                "Giyim": "👕",
                "Kitap": "📚",
                "Mobilya": "🪑"
            }
            
            # Mevcut kategorileri güncelle
            for existing_cat in existing_categories:
                if existing_cat.name in alt_kategori_map:
                    existing_cat.type = "sub"
                    existing_cat.icon = alt_kategori_map[existing_cat.name]
                    existing_cat.parent_id = satis.id  # Varsayılan olarak Satış'a ekle
                    existing_cat.description = f"{existing_cat.name} ürünleri"
                    logger.info(f"Kategori güncellendi: {existing_cat.name}")
            
            # Eksik alt kategorileri ekle
            for name, icon in alt_kategori_map.items():
                # Satış alt kategorisi
                satis_sub = Category.query.filter_by(name=name, parent_id=satis.id).first()
                if not satis_sub:
                    satis_sub = Category(
                        name=name,
                        description=f"{name} ürünleri",
                        type="sub",
                        parent_id=satis.id,
                        icon=icon,
                        is_active=True
                    )
                    db.session.add(satis_sub)
                    logger.info(f"Satış alt kategorisi eklendi: {name}")
                
                # Takas alt kategorisi
                takas_sub = Category.query.filter_by(name=name, parent_id=takas.id).first()
                if not takas_sub:
                    takas_sub = Category(
                        name=name,
                        description=f"{name} ürünleri",
                        type="sub",
                        parent_id=takas.id,
                        icon=icon,
                        is_active=True
                    )
                    db.session.add(takas_sub)
                    logger.info(f"Takas alt kategorisi eklendi: {name}")
            
            db.session.commit()
            logger.info("Tüm kategoriler güncellendi")
            
            # Sonuçları göster
            main_categories = Category.get_main_categories()
            print("\n" + "="*50)
            print("🎯 KATEGORİLER BAŞARIYLA GÜNCELLENDİ!")
            print("="*50)
            
            for main_cat in main_categories:
                print(f"\n🏷️ {main_cat.icon} {main_cat.name}")
                print(f"   📝 {main_cat.description}")
                for sub_cat in main_cat.subcategories:
                    print(f"   ├── {sub_cat.icon} {sub_cat.name}")
                print(f"   └── Toplam: {len(main_cat.subcategories)} alt kategori")
            
            print(f"\n✅ Toplam: {len(main_categories)} ana kategori")
            print("="*50)
            
        except Exception as e:
            logger.error(f"Kategori seed hatası: {str(e)}", exc_info=True)
            db.session.rollback()
            print(f"❌ Hata: {str(e)}")
        finally:
            db.session.close()

if __name__ == "__main__":
    seed_categories()
