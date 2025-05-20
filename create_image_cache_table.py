import os
import sys
from app import create_app, db
from app.models import VocabularyImageCache
from sqlalchemy import inspect

def create_image_cache_table():
    """Tạo bảng VocabularyImageCache nếu chưa tồn tại"""
    app = create_app()
    with app.app_context():
        try:
            # Kiểm tra xem bảng đã tồn tại chưa
            print("Kiểm tra bảng VocabularyImageCache...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'vocabulary_image_cache' in tables:
                print("Bảng VocabularyImageCache đã tồn tại.")
                # Reset bảng - xóa tất cả dữ liệu
                print("Đang xóa dữ liệu cũ trong bảng...")
                db.session.query(VocabularyImageCache).delete()
                db.session.commit()
                print("Đã xóa dữ liệu cũ trong bảng VocabularyImageCache.")
                return 0
            
            # Tạo bảng mới
            print("Bảng VocabularyImageCache chưa tồn tại. Đang tạo bảng...")
            # Tạo bảng cụ thể, không phải tất cả các bảng
            VocabularyImageCache.__table__.create(db.engine, checkfirst=True)
            db.session.commit()
            print("Đã tạo bảng VocabularyImageCache thành công!")
            
            # Kiểm tra lại bằng cách thử tạo một bản ghi
            try:
                # Thử thêm một bản ghi đơn giản để kiểm tra
                test_cache = VocabularyImageCache(
                    word="test",
                    word_type="noun", 
                    topic="test",
                    image_url="https://example.com/test.jpg"
                )
                db.session.add(test_cache)
                db.session.commit()
                
                # Xóa bản ghi test
                db.session.delete(test_cache)
                db.session.commit()
                print("Xác nhận bảng đã được tạo thành công và hoạt động bình thường.")
                return 0
            except Exception as e:
                print(f"Lỗi khi kiểm tra bảng: {str(e)}")
                return 1
                
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi tạo bảng: {str(e)}")
            return 1

if __name__ == "__main__":
    sys.exit(create_image_cache_table()) 