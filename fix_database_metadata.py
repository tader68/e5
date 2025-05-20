#!/usr/bin/env python
"""
This script directly modifies the SQLite database structure to ensure
the extras column is properly defined in the vocabulary_word table.
"""

import os
import sqlite3
import shutil
import subprocess

def backup_database():
    """Create a backup of the database file"""
    from datetime import datetime
    
    # Get timestamp for backup name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    source = "lingoboost.db"
    backup = f"lingoboost.db.bak.{timestamp}"
    
    # Copy the file
    shutil.copy2(source, backup)
    print(f"Created database backup: {backup}")
    return backup

def fix_database():
    """Fix the database schema to ensure extras column exists"""
    print("Connecting to database...")
    
    # Connect to the database
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Check if extras column exists
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns: {', '.join(column_names)}")
    
    # Add extras column if it doesn't exist
    if 'extras' not in column_names:
        print("Adding 'extras' column to vocabulary_word table...")
        try:
            cursor.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
            conn.commit()
            print("✓ Column added successfully")
        except sqlite3.OperationalError as e:
            print(f"Error adding column: {e}")
    else:
        print("✓ 'extras' column already exists in the database")
    
    # Initialize NULL values
    print("Initializing any NULL values in extras column...")
    cursor.execute("UPDATE vocabulary_word SET extras = '{}' WHERE extras IS NULL")
    updated = cursor.rowcount
    conn.commit()
    print(f"✓ Updated {updated} rows with empty JSON objects")
    
    # Check again after changes
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    print("\nFinal table structure:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({col[2]}) {'NOT NULL' if not col[3] else 'NULL'}")
    
    # Close the connection
    conn.close()
    
    print("\nDatabase fix complete!")

def clear_python_cache():
    """Clear all Python cache files"""
    print("Clearing Python cache files...")
    
    # Remove all __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_dir)
            print(f"  Removed {pycache_dir}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                os.remove(pyc_file)
                print(f"  Removed {pyc_file}")
    
    print("✓ Python cache cleared")

def main():
    """Main execution function"""
    print("=== LingoBoost Database Fix ===")
    
    # Step 1: Backup the database
    backup = backup_database()
    
    # Step 2: Clear Python cache
    clear_python_cache()
    
    # Step 3: Fix the database
    fix_database()
    
    print("""
=== Fix Complete ===
Next steps:
1. Stop the Flask application if it's running
2. Run the application again: python app.py

If you encounter issues, you can restore the backup:
copy "{backup}" lingoboost.db
""")

if __name__ == "__main__":
    main() 