#!/usr/bin/env python
"""
Simple reset script for vocabulary_word table to fix the extras column issue
"""
import os
import sys
import shutil
import sqlite3
import importlib
from datetime import datetime

# Create database backup
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
src = "lingoboost.db"
dst = f"lingoboost.db.bak.{timestamp}"

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"✓ Created database backup: {dst}")

# Clear Python cache
for root, dirs, files in os.walk('.'):
    for dir in dirs:
        if dir == '__pycache__':
            for file in os.listdir(os.path.join(root, dir)):
                os.remove(os.path.join(root, dir, file))
            print(f"Cleared cache: {os.path.join(root, dir)}")

# Reset vocabulary_word table
print("\n=== Resetting vocabulary_word table ===")
conn = sqlite3.connect("lingoboost.db")
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
if cursor.fetchone():
    # Get current structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Current columns: {', '.join(column_names)}")
    
    # Extract data
    cursor.execute("SELECT * FROM vocabulary_word")
    rows = cursor.fetchall()
    print(f"Backing up {len(rows)} vocabulary words")
    
    # Create new table
    cursor.execute("DROP TABLE IF EXISTS vocabulary_word_backup")
    cursor.execute("ALTER TABLE vocabulary_word RENAME TO vocabulary_word_backup")
    
    # Create new table with all columns
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
    
    # Recreate indexes
    cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
    cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")
    
    # Transfer data
    if rows:
        print("Transferring data to new table...")
        
        # Get columns from old table
        old_cols = ", ".join(column_names)
        
        # If extras already exists, use it directly
        if 'extras' in column_names:
            cursor.execute(f"INSERT INTO vocabulary_word SELECT {old_cols} FROM vocabulary_word_backup")
        else:
            # If extras doesn't exist, add it with empty JSON
            cursor.execute(f"INSERT INTO vocabulary_word ({old_cols}, extras) SELECT {old_cols}, '{{}}' FROM vocabulary_word_backup")
        
        cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
        
        # Drop backup table
        cursor.execute("DROP TABLE vocabulary_word_backup")
    
    conn.commit()
    
    # Verify new structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    new_columns = cursor.fetchall()
    new_column_names = [col[1] for col in new_columns]
    print(f"New columns: {', '.join(new_column_names)}")
    
    if 'extras' in new_column_names:
        print("✓ extras column now exists in vocabulary_word table")
    else:
        print("✗ Failed to add extras column")
else:
    # Create new table from scratch
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
    
    # Create indexes
    cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
    cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")
    conn.commit()
    
    print("✓ Created new vocabulary_word table")

conn.close()

print("\n=== Reset complete ===")
print("Next step: Restart your Flask application")
print("If the error persists, try to re-create the VocabularyWord model class with the extras column properly defined.") 