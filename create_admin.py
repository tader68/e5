from app import create_app, db
from app.models import User, League
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    # Kiểm tra xem tài khoản admin đã tồn tại chưa
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        # Tạo tài khoản admin mới
        admin = User(
            username='admin',
            email='admin@lingoboost.com',
            level='C2',
            experience_points=1000,
            user_level=10,
            streak_days=30,
            longest_streak=30,
            gems=500,
            last_activity_date=date.today(),
            password_note='Admin@123'  # Lưu mật khẩu ban đầu
        )
        admin.password_hash = generate_password_hash('Admin@123')
        
        # Thêm vào database
        db.session.add(admin)
        db.session.commit()
        
        # Thêm admin vào league cao nhất (Diamond)
        diamond_league = League.query.filter_by(name='Diamond').first()
        if diamond_league:
            from app.models import UserLeague
            from datetime import datetime
            import time
            
            # Lấy số tuần hiện tại trong năm
            week_number = datetime.now().isocalendar()[1]
            
            admin_league = UserLeague(
                user_id=admin.id,
                league_id=diamond_league.id,
                weekly_xp=500,
                weekly_rank=1,
                week_number=week_number,
                joined_date=datetime.utcnow()
            )
            db.session.add(admin_league)
            db.session.commit()
        
        print("Tài khoản admin đã được tạo thành công!")
    else:
        # Cập nhật admin với các trường mới nếu chưa có
        updated = False
        
        # Kiểm tra và cập nhật các trường gamification
        if admin.experience_points is None:
            admin.experience_points = 1000
            updated = True
            
        if admin.user_level is None:
            admin.user_level = 10
            updated = True
            
        if admin.streak_days is None:
            admin.streak_days = 30
            updated = True
            
        if admin.longest_streak is None:
            admin.longest_streak = 30
            updated = True
            
        if admin.gems is None:
            admin.gems = 500
            updated = True
            
        if admin.last_activity_date is None:
            admin.last_activity_date = date.today()
            updated = True
            
        # Thêm admin vào league cao nhất nếu chưa có
        from app.models import UserLeague
        admin_league = UserLeague.query.filter_by(user_id=admin.id).first()
        
        if not admin_league:
            diamond_league = League.query.filter_by(name='Diamond').first()
            if diamond_league:
                from datetime import datetime
                
                # Lấy số tuần hiện tại trong năm
                week_number = datetime.now().isocalendar()[1]
                
                admin_league = UserLeague(
                    user_id=admin.id,
                    league_id=diamond_league.id,
                    weekly_xp=500,
                    weekly_rank=1,
                    week_number=week_number,
                    joined_date=datetime.utcnow()
                )
                db.session.add(admin_league)
                updated = True
                
        if updated:
            db.session.commit()
            print("Tài khoản admin đã được cập nhật với gamification system!")
        else:
            print("Tài khoản admin đã tồn tại và đã cập nhật!")