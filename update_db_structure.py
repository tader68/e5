#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import shutil
import os
from datetime import datetime

# Đường dẫn tới file cơ sở dữ liệu
DB_PATH = 'lingoboost.db'

def backup_database():
    """Tạo bản sao lưu của cơ sở dữ liệu"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{DB_PATH}.bak.{timestamp}"
    
    # Copy file
    with open(DB_PATH, 'rb') as source:
        with open(backup_filename, 'wb') as dest:
            dest.write(source.read())
    
    print(f"Đã tạo bản sao lưu: {backup_filename}")
    return backup_filename

def create_all_tables():
    """Create all necessary tables with proper structure"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create user table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                username VARCHAR(64) UNIQUE,
                email VARCHAR(120) UNIQUE,
                password_hash VARCHAR(128),
                password_note VARCHAR(128),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                avatar_file VARCHAR(255) DEFAULT 'default.png',
                experience_points INTEGER DEFAULT 0,
                user_level INTEGER DEFAULT 1,
                streak_days INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                last_activity_date DATE,
                level VARCHAR(10) DEFAULT 'A1'
            )
        """)
        
        # Create vocabulary_word table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary_word (
                id INTEGER PRIMARY KEY,
                word VARCHAR(100),
                word_type VARCHAR(20),
                phonetics VARCHAR(100),
                meaning TEXT,
                example TEXT,
                level VARCHAR(10),
                topic VARCHAR(100)
            )
        """)
        
        # Create user_vocabulary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_vocabulary (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                word_id INTEGER,
                status VARCHAR(20) DEFAULT 'learning',
                familiarity_level INTEGER DEFAULT 0,
                next_review DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (word_id) REFERENCES vocabulary_word (id)
            )
        """)
        
        # Create vocabulary_image_cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary_image_cache (
                id INTEGER PRIMARY KEY,
                word VARCHAR(100),
                word_type VARCHAR(20),
                topic VARCHAR(100),
                image_url VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(word, word_type, topic)
            )
        """)
        
        # Create grammar_topic table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grammar_topic (
                id INTEGER PRIMARY KEY,
                title VARCHAR(100),
                description TEXT,
                level VARCHAR(10),
                content TEXT
            )
        """)
        
        # Create grammar_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grammar_progress (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                topic_id INTEGER,
                status VARCHAR(20) DEFAULT 'not_started',
                score INTEGER DEFAULT 0,
                last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (topic_id) REFERENCES grammar_topic (id)
            )
        """)
        
        # Create writing_task table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS writing_task (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title VARCHAR(200),
                prompt TEXT,
                content TEXT,
                feedback TEXT,
                level VARCHAR(10),
                task_type VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                grammar_score INTEGER DEFAULT 0,
                vocabulary_score INTEGER DEFAULT 0,
                coherence_score INTEGER DEFAULT 0,
                overall_score INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        
        # Create reading_text table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_text (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200),
                content TEXT,
                level VARCHAR(10),
                topic VARCHAR(100)
            )
        """)
        
        # Create reading_question table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_question (
                id INTEGER PRIMARY KEY,
                text_id INTEGER,
                question_text TEXT,
                question_type VARCHAR(50),
                options TEXT,
                correct_answer TEXT,
                FOREIGN KEY (text_id) REFERENCES reading_text (id)
            )
        """)
        
        # Create reading_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_progress (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                text_id INTEGER,
                score INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (text_id) REFERENCES reading_text (id)
            )
        """)
        
        # Create achievement table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievement (
                id INTEGER PRIMARY KEY,
                name_key VARCHAR(100) UNIQUE,
                description_key VARCHAR(200),
                icon VARCHAR(50),
                category VARCHAR(50),
                xp_reward INTEGER DEFAULT 50,
                gem_reward INTEGER DEFAULT 5,
                condition_type VARCHAR(50),
                condition_value INTEGER
            )
        """)
        
        # Create user_achievement table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievement (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                achievement_id INTEGER,
                earned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (achievement_id) REFERENCES achievement (id)
            )
        """)
        
        # Create league table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS league (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50),
                rank INTEGER
            )
        """)
        
        # Create user_league table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_league (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                league_id INTEGER,
                weekly_xp INTEGER DEFAULT 0,
                weekly_rank INTEGER,
                week_number INTEGER,
                joined_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (league_id) REFERENCES league (id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("All database tables created successfully!")
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Error creating database tables: {str(e)}")

def create_admin_user():
    """Create an admin user if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT id FROM user WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            from werkzeug.security import generate_password_hash
            # Create the admin user
            cursor.execute("""
                INSERT INTO user (username, email, password_hash, level)
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@lingoboost.com', generate_password_hash('Admin@123'), 'C2'))
            conn.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
            
        conn.close()
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Error creating admin user: {str(e)}")

def update_db_structure():
    """Cập nhật cấu trúc cơ sở dữ liệu"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(user_vocabulary)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'collection_id' not in columns:
            print("Thêm cột collection_id vào bảng user_vocabulary...")
            cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN collection_id INTEGER")
            conn.commit()
            print("✅ Đã thêm cột collection_id thành công")
        else:
            print("Cột collection_id đã tồn tại, không cần thêm mới")
        
        # Tạo bảng VocabularyCollection nếu chưa tồn tại
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            topic TEXT,
            level TEXT,
            created_at TIMESTAMP,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );
        """)
        
        # Tạo bảng VocabularyCollectionItem nếu chưa tồn tại
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_collection_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER,
            word_id INTEGER,
            added_at TIMESTAMP,
            FOREIGN KEY (collection_id) REFERENCES vocabulary_collection (id),
            FOREIGN KEY (word_id) REFERENCES vocabulary_word (id)
        );
        """)
        
        conn.commit()
        print("✅ Đã tạo các bảng mới thành công")
        
    except Exception as e:
        conn.rollback()
        print(f"⚠️ Lỗi: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Không tìm thấy cơ sở dữ liệu: {DB_PATH}")
        exit(1)
    
    # Tạo backup trước khi thay đổi
    backup_file = backup_database()
    print(f"Đã sao lưu cơ sở dữ liệu tại: {backup_file}")
    
    # Thực hiện cập nhật
    update_db_structure()
    print("✅ Hoàn tất cập nhật cấu trúc cơ sở dữ liệu") 