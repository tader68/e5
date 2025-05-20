#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db

def backup_database():
    """Tạo bản sao lưu cơ sở dữ liệu trước khi reset"""
    db_path = 'lingoboost.db'
    if os.path.exists(db_path):
        backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print(f"✅ Đã tạo bản sao lưu: {backup_path}")
        return backup_path
    return None

def remove_existing_db():
    """Remove existing database files in both root and instance folder"""
    root_db = 'lingoboost.db'
    instance_db = 'instance/lingoboost.db'
    
    # Remove root db if exists
    if os.path.exists(root_db):
        try:
            os.remove(root_db)
            print(f"Removed existing database: {root_db}")
        except Exception as e:
            print(f"Could not remove {root_db}: {e}")
    
    # Remove instance db if exists
    if os.path.exists(instance_db):
        try:
            os.remove(instance_db)
            print(f"Removed existing database: {instance_db}")
        except Exception as e:
            print(f"Could not remove {instance_db}: {e}")

def create_all_tables():
    """Create all necessary tables with proper structure"""
    try:
        # Connect to the database in root directory
        conn = sqlite3.connect('lingoboost.db')
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
        print("All database tables created successfully!")
        return conn
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Error creating database tables: {str(e)}")
        return None

def create_admin_user(conn):
    """Create an admin user if it doesn't exist"""
    try:
        cursor = conn.cursor()
        
        # Create the admin user
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, level, avatar_file)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin', 'admin@lingoboost.com', generate_password_hash('Admin@123'), 'C2', 'default.png'))
        conn.commit()
        print("Admin user created successfully!")
            
    except Exception as e:
        conn.rollback()
        print(f"Error creating admin user: {str(e)}")

def init_leagues(conn):
    """Initialize league data"""
    try:
        cursor = conn.cursor()
        
        leagues = [
            {'name': 'Bronze', 'rank': 1},
            {'name': 'Silver', 'rank': 2},
            {'name': 'Gold', 'rank': 3},
            {'name': 'Sapphire', 'rank': 4},
            {'name': 'Ruby', 'rank': 5},
            {'name': 'Diamond', 'rank': 6}
        ]
        
        for league_data in leagues:
            cursor.execute(
                "INSERT INTO league (name, rank) VALUES (?, ?)",
                (league_data['name'], league_data['rank'])
            )
        
        conn.commit()
        print(f"Added {len(leagues)} leagues")
            
    except Exception as e:
        conn.rollback()
        print(f"Error initializing leagues: {str(e)}")

def reset_database():
    """Xóa và tạo lại toàn bộ cấu trúc cơ sở dữ liệu"""
    with app.app_context():
        print("🗑️ Đang xóa cấu trúc cơ sở dữ liệu cũ...")
        db.drop_all()
        print("✅ Đã xóa cấu trúc cũ thành công")
        
        print("🔄 Đang tạo cấu trúc cơ sở dữ liệu mới từ mô hình...")
        db.create_all()
        print("✅ Đã tạo cấu trúc mới thành công")
        
        # Tái tạo admin user nếu cần
        # from app.models import User
        # admin = User.query.filter_by(username='admin').first()
        # if not admin:
        #     from werkzeug.security import generate_password_hash
        #     admin = User(username='admin', email='admin@lingoboost.com')
        #     admin.password_hash = generate_password_hash('Admin@123')
        #     db.session.add(admin)
        #     db.session.commit()
        #     print("✅ Đã tạo lại user admin")

if __name__ == '__main__':
    # Tạo backup
    backup_file = backup_database()
    if backup_file:
        print(f"Đã sao lưu cơ sở dữ liệu tại: {backup_file}")
    
    # Reset database
    reset_database()
    print("🎉 Hoàn tất reset cơ sở dữ liệu!") 