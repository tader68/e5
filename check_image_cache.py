import os
import sys
from app import create_app, db
from app.models import VocabularyImageCache
from sqlalchemy import inspect
import time

def check_image_cache():
    """Kiểm tra cấu trúc bảng VocabularyImageCache"""
    app = create_app()
    with app.app_context():
        try:
            # Kiểm tra xem bảng đã tồn tại chưa
            print("Kiểm tra bảng VocabularyImageCache...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'vocabulary_image_cache' in tables:
                print("Bảng VocabularyImageCache tồn tại.")
                
                # Lấy thông tin cột
                columns = inspector.get_columns('vocabulary_image_cache')
                print(f"Số cột: {len(columns)}")
                print("Danh sách các cột:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                # Kiểm tra cột word_hash
                column_names = [col['name'] for col in columns]
                if 'word_hash' in column_names:
                    print("Cột word_hash đã tồn tại.")
                else:
                    print("CẢNH BÁO: Cột word_hash không tồn tại trong bảng!")
                    print("Cần tạo lại bảng với cấu trúc đúng.")
                
                # Kiểm tra số lượng dữ liệu
                count = db.session.query(VocabularyImageCache).count()
                print(f"Số lượng bản ghi: {count}")
                
                # Hiển thị các bản ghi (nếu có)
                if count > 0:
                    limit = min(5, count)
                    print(f"Hiển thị {limit} bản ghi đầu tiên:")
                    records = db.session.query(VocabularyImageCache).limit(limit).all()
                    for record in records:
                        print(f"  - ID: {record.id}, Word: {record.word}, Image: {record.image_url}")
                
                return 0
            else:
                print("Bảng VocabularyImageCache chưa tồn tại!")
                return 1
                
        except Exception as e:
            print(f"Lỗi khi kiểm tra bảng: {str(e)}")
            return 1

if __name__ == "__main__":
    sys.exit(check_image_cache()) 