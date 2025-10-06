from flask import Flask, request, g, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from extensions import db, migrate, jwt, bcrypt
from routes import api_bp
from utils.logger import logger
from datetime import timedelta
import time
import traceback

# Global app instance
app = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES
    
    # Swagger configuration
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Takas Backend API"
        }
    )
    
    # Register blueprints
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Static file serving for uploads
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory('uploads', filename)
    
    # Request logging middleware
    @app.before_request
    def before_request():
        # Record start time
        g.start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url}")
        
        # Log request details - sadece POST/PUT request'lerde JSON kontrol et
        if request.method in ['POST', 'PUT'] and request.is_json and request.get_data():
            try:
                logger.debug(f"Request JSON data: {request.get_json()}")
            except Exception as e:
                logger.debug(f"Request data (not JSON): {request.get_data()}")
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else None
        
        # Log request completion
        logger.log_request(request, response, duration)
        
        return response
    
    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error with full traceback
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        # Log additional context
        context = {
            'request_method': request.method,
            'request_url': request.url,
            'request_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        logger.log_error_with_context(e, context)
        
        return {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }, 500
    
    # Database error handler
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error("Database session rolled back due to error")
        return {
            'error': 'Database error',
            'message': 'A database error occurred'
        }, 500
    
    # Database initialization
    with app.app_context():
        db.create_all()
        
        # Veritabanı migration - image_url sütunu ekle
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                # items tablosuna image_url sütunu ekle (eğer yoksa)
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'items' AND column_name = 'image_url'
                """))
                
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE items ADD COLUMN image_url VARCHAR(500)"))
                    print("image_url sütunu items tablosuna eklendi")
                else:
                    print("image_url sütunu zaten mevcut")
                
                # items tablosuna view_count sütunu ekle (eğer yoksa)
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'items' AND column_name = 'view_count'
                """))
                
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE items ADD COLUMN view_count INTEGER DEFAULT 0"))
                    print("view_count sütunu items tablosuna eklendi")
                else:
                    print("view_count sütunu zaten mevcut")
                
                # product_views tablosunu oluştur (eğer yoksa)
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'product_views'
                """))
                
                if not result.fetchone():
                    conn.execute(text("""
                        CREATE TABLE product_views (
                            id SERIAL PRIMARY KEY,
                            product_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                            viewer_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(product_id, viewer_user_id)
                        )
                    """))
                    print("product_views tablosu oluşturuldu")
                else:
                    print("product_views tablosu zaten mevcut")
                
                # images tablosunu kaldır (eğer varsa)
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'images'
                """))
                
                if result.fetchone():
                    conn.execute(text("DROP TABLE IF EXISTS images CASCADE"))
                    print("images tablosu kaldırıldı")
                else:
                    print("images tablosu zaten yok")
                
                conn.commit()
                
        except Exception as e:
            print(f"Migration hatası: {str(e)}")
        
        print("Veritabanı başlatıldı")
    
    logger.info("Flask application created successfully")
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        logger.info("Starting Flask application...")
        app.run(host=app.config.get('HOST', '0.0.0.0'), port=app.config.get('PORT', 8001), debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}", exc_info=True)
else:
    # Global app instance for import
    app = create_app()
