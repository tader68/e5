import sqlite3
import os
import shutil
from datetime import datetime

def backup_db():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    src = "lingoboost.db"
    dst = f"lingoboost.db.bak.{timestamp}"
    shutil.copy2(src, dst)
    print(f"Database backed up to {dst}")
    return dst

def clear_cache():
    """Remove all __pycache__ directories and .pyc files"""
    print("Clearing Python cache...")
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            try:
                shutil.rmtree(os.path.join(root, '__pycache__'))
            except Exception as e:
                print(f"Error removing __pycache__: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    print(f"Error removing .pyc file: {e}")
    
    print("Cache cleared")

def fix_vocab_table():
    """Fix the vocabulary_word table structure"""
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Check if vocabulary_word table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
    if not cursor.fetchone():
        print("vocabulary_word table doesn't exist! Creating it...")
        cursor.execute("""
        CREATE TABLE vocabulary_word (
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
        cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
        cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")
        conn.commit()
        print("Table created successfully")
        return
        
    # Check if extras column exists
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns: {', '.join(column_names)}")
    
    # Save vocabulary data
    cursor.execute("SELECT * FROM vocabulary_word")
    rows = cursor.fetchall()
    print(f"Backing up {len(rows)} vocabulary words")
    
    if 'extras' not in column_names:
        print("The 'extras' column is missing. Recreating table...")
        
        # Recreate table with extras column
        cursor.execute("ALTER TABLE vocabulary_word RENAME TO vocabulary_word_old")
        
        # Create new table with extras column
        cursor.execute("""
        CREATE TABLE vocabulary_word (
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
        
        # Copy data from old table
        old_columns = ", ".join(column_names)
        cursor.execute(f"""
        INSERT INTO vocabulary_word ({old_columns}, extras)
        SELECT {old_columns}, '{{}}' FROM vocabulary_word_old
        """)
        
        # Recreate indexes
        cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
        cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")
        
        # Drop old table
        cursor.execute("DROP TABLE vocabulary_word_old")
        
        conn.commit()
        print("Table recreated with extras column")
    else:
        print("The 'extras' column already exists. Fixing NULL values...")
        cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
        conn.commit()
        print(f"Updated {cursor.rowcount} rows with empty JSON")
    
    # Verify final table structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Final columns: {', '.join(column_names)}")
    
    conn.close()

if __name__ == "__main__":
    print("=== FIXING EXTRAS COLUMN ISSUE ===")
    
    # Create a backup
    backup_path = backup_db()
    
    # Clear all Python cache
    clear_cache()
    
    # Fix the vocabulary_word table
    fix_vocab_table()
    
    print("""
=== FIX COMPLETE ===
Now restart your Flask application with:
    python app.py
    """) 