#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = 'lingoboost.db'

def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    src = "lingoboost.db"
    dst = f"lingoboost.db.bak.{timestamp}"
    shutil.copy2(src, dst)
    print(f"Database backed up to {dst}")
    return dst

def fix_db_structure():
    """Sửa chữa cấu trúc bảng user_vocabulary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem có cột status bị thiếu không
        cursor.execute("PRAGMA table_info(user_vocabulary)")
        columns = {column[1]: column[0] for column in cursor.fetchall()}
        
        if 'status' not in columns:
            print("⚠️ Phát hiện thiếu cột 'status' trong bảng user_vocabulary")
            
            # Tạo bảng mới với cấu trúc đúng
            print("Tạo bảng tạm thời với cấu trúc đúng...")
            cursor.execute("""
            CREATE TABLE user_vocabulary_new (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                word_id INTEGER,
                status VARCHAR(20) DEFAULT 'learning',
                familiarity_level INTEGER DEFAULT 0,
                next_review DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP,
                collection_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (word_id) REFERENCES vocabulary_word (id),
                FOREIGN KEY (collection_id) REFERENCES vocabulary_collection (id)
            )
            """)
            
            # Sao chép dữ liệu cũ sang bảng mới
            print("Di chuyển dữ liệu...")
            cursor.execute("""
            INSERT INTO user_vocabulary_new (id, user_id, word_id, familiarity_level, next_review, last_practiced, collection_id)
            SELECT id, user_id, word_id, familiarity_level, next_review, last_practiced, collection_id FROM user_vocabulary
            """)
            
            # Cập nhật trạng thái mặc định
            cursor.execute("UPDATE user_vocabulary_new SET status = 'learning'")
            
            # Xóa bảng cũ và đổi tên bảng mới
            print("Thay thế bảng cũ bằng bảng mới...")
            cursor.execute("DROP TABLE user_vocabulary")
            cursor.execute("ALTER TABLE user_vocabulary_new RENAME TO user_vocabulary")
            
            print("✅ Đã sửa chữa cấu trúc bảng user_vocabulary thành công")
        else:
            print("✅ Bảng user_vocabulary có đầy đủ các cột cần thiết")
        
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
        print("✅ Hoàn tất cập nhật cấu trúc cơ sở dữ liệu")
        
    except Exception as e:
        conn.rollback()
        print(f"⚠️ Lỗi: {str(e)}")
        raise
    finally:
        conn.close()

def fix_extras_column():
    print("Checking vocabulary_word table structure...")
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Get current table structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Current columns: {column_names}")
    
    # Check if extras column exists
    if 'extras' in column_names:
        print("✓ 'extras' column already exists")
    else:
        print("Adding 'extras' column to vocabulary_word table...")
        try:
            cursor.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
            conn.commit()
            print("✓ Column added successfully")
        except sqlite3.OperationalError as e:
            print(f"Error adding column: {e}")
            print("Recreating table with correct structure...")
            
            # Save existing data
            cursor.execute("SELECT * FROM vocabulary_word")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(vocabulary_word)")
            columns = cursor.fetchall()
            old_column_names = [col[1] for col in columns]
            
            # Create new table
            cursor.execute("""
            CREATE TABLE vocabulary_word_new (
                id INTEGER PRIMARY KEY,
                word VARCHAR(100),
                word_type VARCHAR(20),
                phonetics VARCHAR(100),
                meaning TEXT,
                example TEXT,
                level VARCHAR(10),
                topic VARCHAR(100),
                extras TEXT
            )
            """)
            
            # Copy data
            for row in rows:
                # Map old data to new structure
                values = []
                for i, name in enumerate(old_column_names):
                    if i < len(row):
                        values.append(row[i])
                
                # Add extras column with empty JSON
                values.append('{}')
                
                # Create placeholders
                placeholders = ', '.join(['?' for _ in range(len(values))])
                
                # Insert into new table
                cursor.execute(f"""
                INSERT INTO vocabulary_word_new 
                (id, word, word_type, phonetics, meaning, example, level, topic, extras)
                VALUES ({placeholders})
                """, values)
            
            # Replace old table
            cursor.execute("DROP TABLE vocabulary_word")
            cursor.execute("ALTER TABLE vocabulary_word_new RENAME TO vocabulary_word")
            
            # Re-create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_word ON vocabulary_word (word)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_topic ON vocabulary_word (topic)")
            
            conn.commit()
            print("✓ Table recreated successfully")
    
    # Initialize null values
    cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
    count = cursor.rowcount
    conn.commit()
    print(f"✓ Updated {count} rows with NULL extras values")
    
    # Check final structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Final columns: {column_names}")
    
    conn.close()

def clear_pycache():
    """Remove all __pycache__ directories"""
    print("Clearing Python cache...")
    count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_dir)
                count += 1
            except Exception as e:
                print(f"Error removing {pycache_dir}: {e}")
    print(f"✓ Removed {count} __pycache__ directories")

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Không tìm thấy cơ sở dữ liệu: {DB_PATH}")
        exit(1)
    
    # Tạo backup trước khi thay đổi
    backup_file = backup_database()
    print(f"Đã sao lưu cơ sở dữ liệu tại: {backup_file}")
    
    # Thực hiện sửa chữa
    fix_db_structure()
    
    # Kiểm tra cấu trúc sau khi sửa
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user_vocabulary)")
    columns = cursor.fetchall()
    print("\nCấu trúc bảng user_vocabulary sau khi sửa:")
    for col in columns:
        print(f"{col[0]}|{col[1]}|{col[2]}|{col[3]}|{col[4]}|{col[5]}")
    conn.close()
    
    # Fix extras column
    fix_extras_column()
    
    # Clear pycache
    clear_pycache()
    
    print("""
=== FIX COMPLETE ===
Now try restarting your application with:
python app.py
""") 