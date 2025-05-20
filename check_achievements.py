from app import create_app, db
from app.models import User, Achievement, UserAchievement, UserVocabulary, GrammarProgress, ReadingProgress, WritingTask, UserLeague
from datetime import datetime
from app.main.routes import award_achievement

def check_achievements():
    """Kiểm tra và cập nhật thành tích dựa vào dữ liệu thực tế của người dùng"""
    app = create_app()
    with app.app_context():
        print("Bắt đầu kiểm tra thành tích...")
        users = User.query.all()
        
        for user in users:
            print(f"\nKiểm tra thành tích cho người dùng: {user.username}")
            
            # ----- STREAK ACHIEVEMENTS -----
            streak_days = user.streak_days or 0
            print(f"Chuỗi học tập hiện tại: {streak_days} ngày")
            
            # Kiểm tra các mốc chuỗi học tập (3, 7, 14, 30, 100, 365 ngày)
            streak_milestones = [3, 7, 14, 30, 100, 365]
            for milestone in streak_milestones:
                if streak_days >= milestone:
                    result = award_achievement(f'streak_{milestone}', user.id)
                    print(f"Thành tích chuỗi {milestone} ngày: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- VOCABULARY ACHIEVEMENTS -----
            vocab_count = UserVocabulary.query.filter_by(user_id=user.id).count()
            mastered_vocab = UserVocabulary.query.filter_by(user_id=user.id, status='mastered').count()
            print(f"Từ vựng đã học: {vocab_count}, Thành thạo: {mastered_vocab}")
            
            # Từ vựng collection milestones
            vocab_milestones = [1, 10, 50, 100, 500]
            vocab_keys = {1: 'first_word', 10: 'collection_10', 50: 'collection_50', 
                          100: 'collection_100', 500: 'collection_500'}
            
            for milestone in vocab_milestones:
                if vocab_count >= milestone:
                    result = award_achievement(vocab_keys[milestone], user.id)
                    print(f"Thành tích {milestone} từ: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # Từ vựng mastered milestones
            mastered_milestones = [1, 10, 50, 100]
            mastered_keys = {1: 'first_mastered', 10: 'mastered_10', 50: 'mastered_50', 
                            100: 'mastered_100'}
            
            for milestone in mastered_milestones:
                if mastered_vocab >= milestone:
                    result = award_achievement(mastered_keys[milestone], user.id)
                    print(f"Thành tích {milestone} từ thành thạo: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- GRAMMAR ACHIEVEMENTS -----
            grammar_count = GrammarProgress.query.filter_by(user_id=user.id, status='completed').count()
            grammar_mastered = GrammarProgress.query.filter_by(user_id=user.id, status='mastered').count()
            print(f"Ngữ pháp đã học: {grammar_count}, Thành thạo: {grammar_mastered}")
            
            # Chủ đề ngữ pháp milestones
            grammar_milestones = [1, 5, 15]
            grammar_keys = {1: 'grammar_first', 5: 'grammar_5', 15: 'grammar_15'}
            
            for milestone in grammar_milestones:
                if grammar_count >= milestone:
                    result = award_achievement(grammar_keys[milestone], user.id)
                    print(f"Thành tích {milestone} chủ đề ngữ pháp: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # Grammar mastery milestones
            grammar_mastery_milestones = [5, 15]
            grammar_mastery_keys = {5: 'grammar_master', 15: 'grammar_expert'}
            
            for milestone in grammar_mastery_milestones:
                if grammar_mastered >= milestone:
                    result = award_achievement(grammar_mastery_keys[milestone], user.id)
                    print(f"Thành tích thành thạo {milestone} chủ đề ngữ pháp: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- WRITING ACHIEVEMENTS -----
            writing_count = WritingTask.query.filter_by(user_id=user.id).count()
            print(f"Bài viết đã làm: {writing_count}")
            
            # Writing milestones
            writing_milestones = [1, 5, 10, 25]
            writing_keys = {1: 'first_essay', 5: 'writing_5', 10: 'writing_expert', 25: 'writing_master'}
            
            for milestone in writing_milestones:
                if writing_count >= milestone:
                    result = award_achievement(writing_keys[milestone], user.id)
                    print(f"Thành tích {milestone} bài viết: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- READING ACHIEVEMENTS -----
            reading_count = ReadingProgress.query.filter_by(user_id=user.id, completed=True).count()
            print(f"Bài đọc đã hoàn thành: {reading_count}")
            
            # Reading milestones
            reading_milestones = [1, 5, 10, 25]
            reading_keys = {1: 'first_reading', 5: 'reading_5', 10: 'reading_expert', 25: 'reading_master'}
            
            for milestone in reading_milestones:
                if reading_count >= milestone:
                    result = award_achievement(reading_keys[milestone], user.id)
                    print(f"Thành tích {milestone} bài đọc: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- LEVEL ACHIEVEMENTS -----
            user_level = user.user_level
            print(f"Cấp độ người dùng: {user_level}")
            
            # Level milestones
            level_milestones = [5, 10, 25]
            level_keys = {5: 'level_5', 10: 'level_10', 25: 'level_25'}
            
            for milestone in level_milestones:
                if user_level >= milestone:
                    result = award_achievement(level_keys[milestone], user.id)
                    print(f"Thành tích cấp độ {milestone}: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
            
            # ----- LEAGUE ACHIEVEMENTS -----
            league_data = user.league_data
            if league_data:
                # League participation
                result = award_achievement('join_league', user.id)
                print(f"Thành tích tham gia giải đấu: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
                
                # League ranking achievements
                weekly_rank = league_data.weekly_rank
                if weekly_rank:
                    print(f"Xếp hạng trong giải đấu: {weekly_rank}")
                    
                    # Top 10
                    if weekly_rank <= 10:
                        result = award_achievement('top_ten', user.id)
                        print(f"Thành tích top 10: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
                    
                    # Top 3
                    if weekly_rank <= 3:
                        result = award_achievement('top_three', user.id)
                        print(f"Thành tích top 3: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
                    
                    # Winner (rank 1)
                    if weekly_rank == 1:
                        result = award_achievement('league_winner', user.id)
                        print(f"Thành tích vô địch giải đấu: {'Đã thêm' if result else 'Đã có hoặc không thể thêm'}")
        
        print("\nKiểm tra thành tích hoàn tất!")

if __name__ == "__main__":
    check_achievements() 