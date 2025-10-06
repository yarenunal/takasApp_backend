HEAD
# takasApp_backend

# Takas Backend

İkinci el takas mobil uygulaması için Python Flask tabanlı REST API backend'i.

## Özellikler

- 🔐 JWT tabanlı kimlik doğrulama
- 👥 Kullanıcı yönetimi (kayıt, giriş, profil)
- 📦 Ürün yönetimi (ekleme, düzenleme, silme)
- 🏷️ Kategori sistemi
- 🤝 Takas teklifleri
- 💬 Mesajlaşma sistemi
- 🗄️ SQLAlchemy ile veritabanı yönetimi
- 🚀 CORS desteği
- 📚 **Swagger/OpenAPI dokümantasyonu**
- 📝 **Kapsamlı logging sistemi**

## 🚀 Swagger API Dokümantasyonu

Uygulama çalıştıktan sonra Swagger UI'a erişim:

**URL:** `http://localhost:8000/swagger`

Swagger UI sayesinde:
- ✅ Tüm API endpoint'lerini görüntüleme
- ✅ API'yi interaktif olarak test etme
- ✅ Request/Response şemalarını inceleme
- ✅ Authentication bilgilerini görme
- ✅ Örnek request'leri kopyalama

## Kurulum

### Gereksinimler

- Python 3.8+
- pip

### Adımlar

1. **Virtual environment oluşturun:**
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python3 app.py
```

Uygulama `http://localhost:8000` adresinde çalışacaktır.

## 📖 API Dokümantasyonu

### Swagger UI
- **URL:** `http://localhost:8000/swagger`
- **Açıklama:** Interaktif API dokümantasyonu ve test arayüzü

### Manuel API Endpoints

#### Kimlik Doğrulama
- `POST /api/v1/auth/register` - Kullanıcı kaydı
- `POST /api/v1/auth/login` - Kullanıcı girişi
- `GET /api/v1/auth/profile` - Profil bilgileri

#### Ürünler
- `GET /api/v1/products/` - Ürünleri listele
- `GET /api/v1/products/<id>` - Ürün detayları
- `POST /api/v1/products/` - Yeni ürün ekle
- `PUT /api/v1/products/<id>` - Ürün güncelle
- `DELETE /api/v1/products/<id>` - Ürün sil

#### Kategoriler
- `GET /api/v1/categories/` - Kategorileri listele
- `GET /api/v1/categories/<id>` - Kategori detayları

#### Takaslar
- `GET /api/v1/trades/` - Takas tekliflerini listele
- `POST /api/v1/trades/` - Yeni takas teklifi oluştur
- `PUT /api/v1/trades/<id>/status` - Takas durumunu güncelle

#### Mesajlar
- `GET /api/v1/messages/` - Mesajları listele
- `POST /api/v1/messages/` - Yeni mesaj gönder
- `PUT /api/v1/messages/<id>/read` - Mesajı okundu olarak işaretle

## 📝 Logging Sistemi

Uygulama kapsamlı logging sistemi ile gelir:

- **Console logları** - Renkli, okunabilir loglar
- **Dosya logları** - `logs/takas_backend.log`
- **Hata logları** - `logs/errors.log`
- **Request tracking** - Her HTTP isteği loglanır
- **Database işlemleri** - Tüm veritabanı operasyonları loglanır
- **Kullanıcı işlemleri** - Kullanıcı eylemleri detaylı loglanır

## 🔧 Geliştirme

### Test Çalıştırma
```bash
pytest
```

### Kod Formatı
```bash
black .
flake8 .
```

### Veritabanı Migrasyonu
```bash
flask db migrate -m "Migration description"
flask db upgrade
```

## 📁 Proje Yapısı

```
takasBackend/
├── app.py                 # Ana uygulama dosyası
├── config.py              # Konfigürasyon ayarları
├── extensions.py          # Flask extension'ları
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
├── static/               # Statik dosyalar
│   └── swagger.json      # Swagger API dokümantasyonu
├── logs/                 # Log dosyaları
│   ├── takas_backend.log # Genel loglar
│   └── errors.log        # Hata logları
├── models/               # Veritabanı modelleri
│   ├── __init__.py
│   ├── user.py           # Kullanıcı modeli
│   ├── product.py        # Ürün modeli
│   ├── category.py       # Kategori modeli
│   ├── trade.py          # Takas modeli
│   └── message.py        # Mesaj modeli
├── routes/               # API route'ları
│   ├── __init__.py
│   ├── auth.py           # Kimlik doğrulama
│   ├── products.py       # Ürün yönetimi
│   ├── categories.py     # Kategori yönetimi
│   ├── trades.py         # Takas yönetimi
│   └── messages.py       # Mesajlaşma
└── utils/                # Yardımcı araçlar
    └── logger.py         # Logging sistemi
```

## 🌟 Öne Çıkan Özellikler

- **Swagger UI** - Interaktif API dokümantasyonu
- **Kapsamlı Logging** - Tüm işlemler detaylı loglanır
- **JWT Authentication** - Güvenli kimlik doğrulama
- **Database Models** - İlişkisel veritabanı yapısı
- **Error Handling** - Kapsamlı hata yönetimi
- **CORS Support** - Cross-origin istek desteği

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Log dosyalarını kontrol edin (`logs/` dizini)
2. Swagger UI'da API'yi test edin
3. Console loglarını inceleyin

## Lisans

Bu projenin her hakkı gizlidir.
50a55fe (Initial commit)
