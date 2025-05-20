from app import create_app, db
from app.models import User, Achievement, UserAchievement
from datetime import datetime

def add_achievements():
    """Thêm thành tích mẫu cho người dùng đầu tiên"""
    app = create_app()
    with app.app_context():
        # Lấy user đầu tiên
        user = User.query.first()
        if not user:
            print("Không tìm thấy người dùng!")
            return
            
        print(f"Thêm thành tích cho người dùng: {user.username}")
        
        # Thêm một số thành tích ví dụ (ID 1, 6, 10)
        achievements = Achievement.query.filter(Achievement.id.in_([1, 6, 10])).all()
        
        for ach in achievements:
            # Kiểm tra xem người dùng đã có thành tích này chưa
            existing = UserAchievement.query.filter_by(
                user_id=user.id, achievement_id=ach.id
            ).first()
            
            if existing:
                print(f"Người dùng đã có thành tích: {ach.name_key}")
                continue
                
            # Thêm thành tích
            user_ach = UserAchievement(
                user_id=user.id,
                achievement_id=ach.id,
                earned_date=datetime.utcnow()
            )
            
            db.session.add(user_ach)
            print(f"Đã thêm thành tích: {ach.name_key}")
        
        # Lưu vào database
        db.session.commit()
        print("Thêm thành tích thành công!")
        
        # Hiển thị tất cả thành tích người dùng đã đạt được
        user_achievements = UserAchievement.query.filter_by(user_id=user.id).all()
        print(f"\nDanh sách thành tích đã đạt được ({len(user_achievements)}):")
        for ua in user_achievements:
            ach = Achievement.query.get(ua.achievement_id)
            print(f"- {ach.name_key} - {ach.icon}")

if __name__ == "__main__":
    add_achievements() 