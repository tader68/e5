import os
from dotenv import load_dotenv
from datetime import timedelta

# Cố gắng load .env file, bỏ qua nếu có lỗi
try:
    load_dotenv()
except:
    pass

# Lấy đường dẫn tuyệt đối đến thư mục gốc
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'LingoBoostSecretKey2024')
    
    # Đảm bảo sử dụng đường dẫn tuyệt đối và chỉ định đường dẫn đầy đủ
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///lingoboost.db'
    
    # Disable SQLAlchemy's event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Force SQLAlchemy to not cache metadata to ensure schema changes are detected
    SQLALCHEMY_ECHO = True  # Log all SQL queries for debugging
    
    # Uploads configuration
    UPLOADS_DEFAULT_DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    UPLOADS_DEFAULT_URL = 'static/uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Avatar uploads directory
    AVATAR_UPLOAD_DIR = os.path.join('app', 'static', 'uploads', 'avatars')
    
    # Admin dictionary path
    ADMIN_DICT_PATH = os.path.join('app', 'admin', 'admin_dict.json')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # Exercise configuration
    VOCABULARY_EXERCISE_COUNT = 10
    GRAMMAR_EXERCISE_COUNT = 10
    
    # Gemini API configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBSUsp00REJ0I6ZeI3B9Bta_Ix_wM63_qs')
    
    # Pagination configuration
    WORDS_PER_PAGE = 20
    
    # Tắt cổng thư mục instance của Flask
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INSTANCE_RELATIVE_CONFIG = False
    # Sử dụng API key từ môi trường hoặc giá trị mặc định nếu không có
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyBNU2IteZpqb93aISVU38Z0fN9r_Wc3_qs')
    
    # Thêm Unsplash API
    UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY', '') 