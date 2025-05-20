from app import create_app, db
from app.models import User, Achievement, UserAchievement

def reset_achievements():
    """Xóa tất cả thành tích đã thêm cho người dùng"""
    app = create_app()
    with app.app_context():
        # Đếm số lượng thành tích trước khi xóa
        count_before = UserAchievement.query.count()
        print(f"Số lượng thành tích trước khi xóa: {count_before}")
        
        # Xóa tất cả thành tích
        UserAchievement.query.delete()
        db.session.commit()
        
        # Đếm số lượng thành tích sau khi xóa
        count_after = UserAchievement.query.count()
        print(f"Số lượng thành tích sau khi xóa: {count_after}")
        print(f"Đã xóa {count_before - count_after} thành tích")
        
        print("Reset thành tích hoàn tất!")

if __name__ == "__main__":
    reset_achievements() 