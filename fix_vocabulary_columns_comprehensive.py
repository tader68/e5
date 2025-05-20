#!/usr/bin/env python
"""
This script provides a comprehensive fix for the vocabulary_word table
by recreating it with the correct structure if needed.
"""

import os
import sqlite3
import shutil
import json
from datetime import datetime

def backup_database():
    """Create a backup of the database file"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    source = "lingoboost.db"
    backup = f"lingoboost.db.bak.{timestamp}"
    
    shutil.copy2(source, backup)
    print(f"Created database backup: {backup}")
    return backup

def fix_vocabulary_table():
    """Fix the vocabulary_word table structure"""
    print("Connecting to database...")
    
    # Connect to the database
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Check current table structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_info = {col[1]: col for col in columns}
    
    print(f"Current columns: {', '.join(column_info.keys())}")
    
    # Method 1: Try adding the column if it doesn't exist
    if 'extras' not in column_info:
        print("Method 1: Adding extras column...")
        try:
            cursor.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
            conn.commit()
            print("✓ Column added successfully via ALTER TABLE")
            
            # Check if column was added
            cursor.execute("PRAGMA table_info(vocabulary_word)")
            columns = cursor.fetchall()
            column_info = {col[1]: col for col in columns}
            
            if 'extras' not in column_info:
                print("✗ Column was not added properly, moving to Method 2")
                method_1_success = False
            else:
                method_1_success = True
        except sqlite3.OperationalError as e:
            print(f"Error in Method 1: {e}")
            method_1_success = False
    else:
        print("✓ extras column already exists")
        method_1_success = True
    
    # Method 2: Recreate the table if Method 1 failed
    if not method_1_success:
        print("\nMethod 2: Recreating the vocabulary_word table with proper structure...")
        
        # Get all existing data
        cursor.execute("SELECT * FROM vocabulary_word")
            rows = cursor.fetchall()
            
        # Get column names for the current table
        cursor.execute("PRAGMA table_info(vocabulary_word)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Backing up {len(rows)} rows of data...")
        
        # Create a temporary table with the correct structure
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
            
        # Insert data into the new table
                for row in rows:
            # Convert row to a dictionary for easier access
            row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
            
            # Prepare values for the new table (include extras as empty JSON if not exists)
            values = [
                row_dict.get('id'),
                row_dict.get('word'),
                row_dict.get('word_type'),
                row_dict.get('phonetics'),
                row_dict.get('meaning'),
                row_dict.get('example'),
                row_dict.get('level'),
                row_dict.get('topic'),
                row_dict.get('extras', '{}')
            ]
            
            # Insert into new table
            cursor.execute("""
            INSERT INTO vocabulary_word_new 
            (id, word, word_type, phonetics, meaning, example, level, topic, extras)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
        
        conn.commit()
        
        # Rename tables to swap them
        print("Swapping tables...")
        cursor.execute("DROP TABLE vocabulary_word")
        cursor.execute("ALTER TABLE vocabulary_word_new RENAME TO vocabulary_word")
        
        # Create indexes that existed on the original table
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_word ON vocabulary_word (word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_topic ON vocabulary_word (topic)")
        
        conn.commit()
        print("✓ Table recreated successfully with extras column")
    
    # Initialize any NULL values in extras column
    print("\nInitializing any NULL values in extras column...")
    cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
    updated = cursor.rowcount
    conn.commit()
    print(f"✓ Updated {updated} rows with empty JSON objects")
    
    # Check final table structure
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    print("\nFinal table structure:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({col[2]}) {'NOT NULL' if not col[3] else 'NULL'}")
    
    # Close connection
    conn.close()

def clear_python_cache():
    """Clear all Python cache files"""
    print("Clearing Python cache files...")
    
    # Remove all __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_dir)
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                os.remove(pyc_file)
    
    print("✓ Python cache cleared")

def main():
    """Main execution function"""
    print("=== LingoBoost Vocabulary Table Fix ===")
    
    # Step 1: Backup the database
    backup = backup_database()
    
    # Step 2: Clear Python cache
    clear_python_cache()
    
    # Step 3: Fix the vocabulary table
    fix_vocabulary_table()
    
    print("""
=== Fix Complete ===
Next steps:
1. Stop the Flask application if it's running
2. Run the application again: python app.py
""")

if __name__ == "__main__":
    main() 