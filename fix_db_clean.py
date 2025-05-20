#!/usr/bin/env python
"""
Create a completely fresh database with the correct structure.
This is a clean approach that rebuilds the database from scratch.
"""
import os
import sys
import shutil
import sqlite3
from datetime import datetime

print("=== REBUILDING DATABASE FROM SCRATCH ===")

# 1. Create backup
if os.path.exists("lingoboost.db"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"lingoboost.db.bak.{timestamp}"
    shutil.copy2("lingoboost.db", backup_path)
    print(f"✓ Created backup: {backup_path}")
    
    # Remove existing database
    os.remove("lingoboost.db")
    print("✓ Removed old database")

# 2. Create fresh database
conn = sqlite3.connect("lingoboost.db")
cursor = conn.cursor()

# 3. Create tables - focusing on vocabulary_word first
print("Creating vocabulary_word table...")
cursor.execute("""
CREATE TABLE vocabulary_word (
    id INTEGER PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    word_type VARCHAR(20),
    phonetics VARCHAR(100),
    meaning TEXT,
    example TEXT,
    level VARCHAR(10),
    topic VARCHAR(100),
    extras TEXT
)
""")

# 4. Create necessary indexes
cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")

# 5. Create other required tables
print("Creating user table...")
cursor.execute("""
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(128),
    full_name VARCHAR(100),
    avatar VARCHAR(200),
    is_admin BOOLEAN,
    last_seen TIMESTAMP,
    password_note VARCHAR(50)
)
""")

print("Creating user_vocabulary table...")
cursor.execute("""
CREATE TABLE user_vocabulary (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    word_id INTEGER,
    status VARCHAR(20),
    familiarity INTEGER,
    last_practiced TIMESTAMP,
    next_review TIMESTAMP,
    collection_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(word_id) REFERENCES vocabulary_word(id)
)
""")

# Add any other required tables
# ...

# Commit changes and close connection
conn.commit()

# Verify tables were created
print("\nVerifying created tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")
    
    # Check columns for vocabulary_word
    if table[0] == 'vocabulary_word':
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

conn.close()

print("\n=== DATABASE REBUILD COMPLETE ===")
print("\nNext steps:")
print("1. Clear all Python cache with: python -m compileall .")
print("2. Restart your Flask application with: python app.py") 