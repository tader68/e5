import os
import sys
from datetime import datetime

from app import create_app, db
from app.models import VocabularyImageCache

def clear_image_cache():
    """Xóa toàn bộ cache hình ảnh để áp dụng thứ tự ưu tiên mới"""
    app = create_app()
    with app.app_context():
        try:
            # Đếm số lượng cache hiện có
            cache_count = VocabularyImageCache.query.count()
            print(f"Số lượng cache hình ảnh hiện tại: {cache_count}")
            
            if cache_count == 0:
                print("Không có cache hình ảnh để xóa.")
                return
            
            # Tạo backup trước khi xóa (tùy chọn)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            print(f"Đang xóa tất cả {cache_count} cache hình ảnh...")
            
            # Xóa tất cả bản ghi
            VocabularyImageCache.query.delete()
            db.session.commit()
            
            # Kiểm tra lại
            new_count = VocabularyImageCache.query.count()
            print(f"Xóa thành công! Số lượng cache còn lại: {new_count}")
            print("Giờ đây hệ thống sẽ ưu tiên sử dụng Pixabay API để lấy hình ảnh.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi xóa cache: {str(e)}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(clear_image_cache()) 