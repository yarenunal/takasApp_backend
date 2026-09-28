# 🔄 TakasApp Backend

**REST API Backend for a Second-Hand Exchange Application**

TakasApp mobil uygulaması için **Python Flask** kullanılarak geliştirilen REST API backend'i. Kullanıcı, ürün, kategori, takas ve mesajlaşma süreçlerini yönetir.

## 🛠️ Tech Stack

* **Backend:** Python, Flask, REST API
* **Database:** SQLAlchemy
* **Authentication:** JWT
* **Documentation:** Swagger / OpenAPI
* **Infrastructure:** CORS
* **Testing & Code Quality:** Pytest, Black, Flake8

## ✨ Features

* 🔐 JWT tabanlı kimlik doğrulama
* 👤 Kullanıcı ve profil yönetimi
* 📦 Ürün ve kategori yönetimi
* 🤝 Takas teklifleri
* 💬 Mesajlaşma sistemi
* 📚 Swagger/OpenAPI ile API dokümantasyonu
* 📝 Request, database ve error logging
* ⚠️ Hata yönetimi ve CORS desteği

## 📚 API Documentation

Uygulama çalıştırıldıktan sonra Swagger UI üzerinden API endpoint'leri görüntülenebilir ve test edilebilir:

```text
http://localhost:8000/swagger
```

## 🎥 Video Sunum

[TakasApp Video Sunumu](https://www.youtube.com/watch?v=Kkcq81ZbU7M)

## 🚀 Installation

### Requirements

* Python 3.8+
* pip

### Setup

```bash
git clone <repository-url>
cd takasApp_backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 app.py
```

API:

```text
http://localhost:8000
```

## 📁 Project Structure

```text
takasApp_backend/
├── app.py
├── config.py
├── extensions.py
├── models/
├── routes/
├── utils/
├── static/
├── logs/
├── requirements.txt
└── README.md
```

## 👩‍💻 Developer

**Yaren Ünal**

Computer Engineer | iOS & Full-Stack Developer | AI-Integrated Applications
