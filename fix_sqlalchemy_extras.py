#!/usr/bin/env python
"""
A comprehensive diagnostic and repair script for the SQLAlchemy 'extras' column issue.
This script will:
1. Check if the extras column exists in the database
2. Verify if SQLAlchemy correctly recognizes the column
3. Fix any metadata caching issues
4. Test a sample query involving the extras column
5. Reset SQLAlchemy metadata and recreate connections if needed
"""

import os
import sys
import importlib
import json
import sqlite3
from datetime import datetime

# Backup database before running fixes
def backup_database():
    """Create a backup of the database file"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    src = "lingoboost.db"
    dst = f"lingoboost.db.bak.{timestamp}"
    
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)
        print(f"✓ Created database backup: {dst}")
        return True
    else:
        print("✗ Database file not found, cannot create backup")
        return False

def check_database_structure():
    """Directly check database structure using sqlite3"""
    print("\n=== Checking Database Structure ===")
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Check if vocabulary_word table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
    if not cursor.fetchone():
        print("✗ vocabulary_word table doesn't exist in the database!")
        conn.close()
        return False
    
    # Check table structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Table columns: {', '.join(column_names)}")
    
    if 'extras' in column_names:
        print("✓ 'extras' column exists in the database schema")
        
        # Check if there are any NULL values in extras column
        cursor.execute("SELECT COUNT(*) FROM vocabulary_word WHERE extras IS NULL")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"! Found {null_count} rows with NULL extras, fixing...")
            cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
            conn.commit()
            print("✓ Fixed NULL values in extras column")
    else:
        print("✗ 'extras' column is MISSING from the database schema")
        
        # Add the column
        try:
            cursor.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
            conn.commit()
            print("✓ Added extras column to the database schema")
        except sqlite3.OperationalError as e:
            print(f"✗ Failed to add extras column: {e}")
            conn.close()
            return False
    
    # Check for sample data
    cursor.execute("SELECT COUNT(*) FROM vocabulary_word")
    count = cursor.fetchone()[0]
    print(f"Total vocabulary words: {count}")
    
    if count > 0:
        # Check a sample row
        cursor.execute("SELECT id, word, word_type, extras FROM vocabulary_word LIMIT 1")
        sample = cursor.fetchone()
        print(f"Sample word: id={sample[0]}, word='{sample[1]}', type='{sample[2]}', extras='{sample[3]}'")
    
    conn.close()
    return True

def check_sqlalchemy_model():
    """Check if SQLAlchemy model includes the extras column"""
    print("\n=== Checking SQLAlchemy Model ===")
    
    # Force reload the app module
    if 'app' in sys.modules:
        del sys.modules['app']
    if 'app.models' in sys.modules:
        del sys.modules['app.models']
    
    # Import required modules
    try:
        from app import create_app, db
        from sqlalchemy import inspect
        app = create_app()
        
        with app.app_context():
            print("App context created successfully")
            
            # Import the VocabularyWord model
            from app.models import VocabularyWord
            
            # Check model attributes
            model_attrs = dir(VocabularyWord)
            if 'extras' in model_attrs:
                print("✓ 'extras' attribute exists in VocabularyWord model")
            else:
                print("✗ 'extras' attribute is MISSING from VocabularyWord model")
            
            # Check table columns in SQLAlchemy metadata
            table_columns = [c.name for c in VocabularyWord.__table__.columns]
            print(f"Model table columns: {', '.join(table_columns)}")
            
            if 'extras' in table_columns:
                print("✓ 'extras' column exists in SQLAlchemy table metadata")
            else:
                print("✗ 'extras' column is MISSING from SQLAlchemy table metadata")
                
            # Check Inspector's view of the database
            inspector = inspect(db.engine)
            db_columns = [c['name'] for c in inspector.get_columns('vocabulary_word')]
            print(f"Inspector columns: {', '.join(db_columns)}")
            
            if 'extras' in db_columns:
                print("✓ 'extras' column exists in Inspector's view")
            else:
                print("✗ 'extras' column is MISSING from Inspector's view")
            
            return 'extras' in model_attrs and 'extras' in table_columns
    except Exception as e:
        print(f"✗ Error checking SQLAlchemy model: {e}")
        return False

def fix_sqlalchemy_metadata():
    """Fix SQLAlchemy metadata to recognize the extras column"""
    print("\n=== Fixing SQLAlchemy Metadata ===")
    
    # Force reload the app module
    if 'app' in sys.modules:
        del sys.modules['app']
    if 'app.models' in sys.modules:
        del sys.modules['app.models']
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Clear and reload metadata
            db.metadata.clear()
            db.reflect()
            
            # Import the VocabularyWord model
            from app.models import VocabularyWord
            
            # Check if extras attribute exists now
            if hasattr(VocabularyWord, 'extras'):
                print("✓ SQLAlchemy now recognizes the extras column")
                return True
            else:
                print("✗ SQLAlchemy still doesn't recognize the extras column")
                return False
    except Exception as e:
        print(f"✗ Error fixing SQLAlchemy metadata: {e}")
        return False

def test_extras_query():
    """Test querying the extras column"""
    print("\n=== Testing Extras Column Query ===")
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Import the VocabularyWord model
            from app.models import VocabularyWord
            
            # Try to query using the extras column
            try:
                # Get one word with non-null extras
                word = VocabularyWord.query.filter(VocabularyWord.extras != None).first()
                
                if word:
                    print(f"✓ Successfully queried word with extras: {word.word}")
                    if hasattr(word, 'extras'):
                        print(f"✓ Extras content: {word.extras}")
                    else:
                        print("✗ Word object does not have 'extras' attribute")
                else:
                    # If no word with extras, try inserting one
                    print("! No words with extras found, creating a test word")
                    test_word = VocabularyWord(
                        word="test_extras",
                        word_type="noun",
                        meaning="A test word for extras column",
                        extras=json.dumps({"test": True})
                    )
                    db.session.add(test_word)
                    db.session.commit()
                    print("✓ Test word with extras created successfully")
                
                return True
            except Exception as e:
                print(f"✗ Query error: {e}")
                return False
    except Exception as e:
        print(f"✗ Error setting up test: {e}")
        return False

def recreate_table_with_extras():
    """Completely recreate the vocabulary_word table with the extras column"""
    print("\n=== Recreating Vocabulary Table ===")
    
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    try:
        # Get data from original table
        cursor.execute("SELECT * FROM vocabulary_word")
        rows = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(vocabulary_word)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Backing up {len(rows)} vocabulary words with columns: {', '.join(column_names)}")
        
        # Create a new table with proper structure
        cursor.execute("DROP TABLE IF EXISTS vocabulary_word_new")
        cursor.execute("""
        CREATE TABLE vocabulary_word_new (
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
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_new_word ON vocabulary_word_new (word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_new_topic ON vocabulary_word_new (topic)")
        
        # Copy data to new table
        placeholders = ", ".join(["?"] * len(column_names))
        
        for row in rows:
            # For each row, ensure we have a valid extras value
            row_data = list(row)
            if 'extras' in column_names:
                extras_idx = column_names.index('extras')
                if row_data[extras_idx] is None:
                    row_data[extras_idx] = '{}'
            else:
                # If extras wasn't in original table, add it
                row_data.append('{}')
                column_names.append('extras')
            
            # Build the INSERT statement dynamically
            insert_columns = ", ".join(column_names)
            cursor.execute(f"INSERT INTO vocabulary_word_new ({insert_columns}) VALUES ({placeholders})", row_data)
        
        # Rename tables
        cursor.execute("DROP TABLE vocabulary_word")
        cursor.execute("ALTER TABLE vocabulary_word_new RENAME TO vocabulary_word")
        
        # Recreate indexes on the new table
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_word ON vocabulary_word (word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_topic ON vocabulary_word (topic)")
        
        conn.commit()
        print(f"✓ Successfully recreated vocabulary_word table with {len(rows)} rows")
        
        # Verify the new table
        cursor.execute("PRAGMA table_info(vocabulary_word)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        print(f"New table columns: {', '.join(new_column_names)}")
        
        if 'extras' in new_column_names:
            print("✓ extras column exists in the new table")
            return True
        else:
            print("✗ Failed to add extras column to the new table")
            return False
    except Exception as e:
        print(f"✗ Error recreating table: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def run_all_checks_and_fixes():
    """Run all diagnostic checks and fixes"""
    print("=== SQLAlchemy Extras Column Diagnostic ===")
    
    # Always backup first
    backup_database()
    
    # Step 1: Check database structure
    db_check = check_database_structure()
    if not db_check:
        print("! Database structure issue detected, attempting to fix...")
        recreate_table_with_extras()
    
    # Step 2: Check SQLAlchemy model
    model_check = check_sqlalchemy_model()
    if not model_check:
        print("! SQLAlchemy model issue detected, attempting to fix...")
        fix_sqlalchemy_metadata()
    
    # Step 3: Test querying the extras column
    query_check = test_extras_query()
    if not query_check:
        print("! Query issue detected, attempting to recreate the table...")
        recreate_table_with_extras()
        # Refresh SQLAlchemy metadata again
        fix_sqlalchemy_metadata()
        # Try the query test again
        test_extras_query()
    
    print("\n=== Diagnostic Complete ===")
    print("Restart your Flask application now to apply all fixes.")

if __name__ == "__main__":
    run_all_checks_and_fixes() 