import os
import sys
import hashlib
from datetime import datetime
from sqlalchemy import text, inspect
from app import create_app, db
from app.models import VocabularyImageCache

def fix_image_cache_structure():
    """
    Fix the VocabularyImageCache table by recreating it with the correct columns,
    including word_hash and updated_at, which are used by the code.
    """
    app = create_app()
    with app.app_context():
        try:
            # Kiểm tra cấu trúc bảng hiện tại
            print("Kiểm tra cấu trúc bảng VocabularyImageCache hiện tại...")
            inspector = inspect(db.engine)
            
            if 'vocabulary_image_cache' in inspector.get_table_names():
                # Backup dữ liệu hiện tại
                print("Sao lưu dữ liệu hiện tại...")
                
                # Lấy danh sách cột hiện tại 
                columns = [col['name'] for col in inspector.get_columns('vocabulary_image_cache')]
                print(f"Cột hiện tại: {columns}")
                
                # Thử select tất cả dữ liệu hiện tại
                existing_data = []
                try:
                    result = db.session.execute(text("SELECT * FROM vocabulary_image_cache"))
                    for row in result:
                        # Convert to dict
                        item = {}
                        for idx, col in enumerate(result.keys()):
                            item[col] = row[idx]
                        existing_data.append(item)
                    print(f"Đã tìm thấy {len(existing_data)} bản ghi để sao lưu")
                except Exception as e:
                    print(f"Không thể đọc dữ liệu hiện tại: {str(e)}")
                    existing_data = []

                # Drop bảng hiện tại
                print("Đang xóa bảng cũ...")
                db.session.execute(text("DROP TABLE IF EXISTS vocabulary_image_cache"))
                db.session.commit()
                
            # Tạo lại bảng với cấu trúc mới
            print("Đang tạo lại bảng với cấu trúc đúng...")
            VocabularyImageCache.__table__.create(db.engine, checkfirst=True)
            db.session.commit()
            
            # Insert lại dữ liệu nếu có
            if existing_data:
                print("Đang khôi phục dữ liệu...")
                for item in existing_data:
                    try:
                        # Tạo word_hash từ từ vựng
                        word = item.get('word', '')
                        word_hash = hashlib.md5(word.lower().encode()).hexdigest() if word else ''
                        
                        # Tạo bản ghi mới với các trường hiện tại + các trường mới
                        cache_entry = VocabularyImageCache(
                            word=word,
                            word_hash=word_hash,
                            word_type=item.get('word_type', 'default'),
                            topic=item.get('topic', 'default'),
                            image_url=item.get('image_url', ''),
                            created_at=item.get('created_at', datetime.utcnow()),
                            updated_at=datetime.utcnow()
                        )
                        db.session.add(cache_entry)
                    except Exception as insert_err:
                        print(f"Lỗi khi khôi phục bản ghi: {str(insert_err)}")
                
                db.session.commit()
                print(f"Đã khôi phục {len(existing_data)} bản ghi")
            
            # Kiểm tra cấu trúc mới
            print("\nCấu trúc mới của bảng:")
            for col in inspector.get_columns('vocabulary_image_cache'):
                print(f"  - {col['name']}: {col['type']}")
            
            print("\nĐã sửa xong cấu trúc bảng VocabularyImageCache!")
            return 0
            
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi sửa bảng: {str(e)}")
            return 1

if __name__ == "__main__":
    sys.exit(fix_image_cache_structure()) 