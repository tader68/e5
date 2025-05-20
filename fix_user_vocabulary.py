import sqlite3
import os
from datetime import datetime
import shutil

# Configuration
DATABASE_PATH = 'lingoboost.db'

def create_backup():
    """Create a backup of the database before making changes"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{DATABASE_PATH}.bak.{timestamp}"
    
    try:
        shutil.copy2(DATABASE_PATH, backup_filename)
        print(f"Created backup: {backup_filename}")
        return True
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False

def check_column_exists(conn, table, column):
    """Check if a column exists in the specified table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    column_names = [column_info[1] for column_info in columns]
    return column in column_names

def add_collection_id_column():
    """Add collection_id column to user_vocabulary table if it doesn't exist"""
    try:
        # Create backup
        if not create_backup():
            return False
            
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if collection_id column already exists
        if check_column_exists(conn, 'user_vocabulary', 'collection_id'):
            print("Column 'collection_id' already exists in table 'user_vocabulary'")
            return True
            
        # Add the column
        cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN collection_id INTEGER REFERENCES vocabulary_collection(id)")
        conn.commit()
        
        print("Successfully added 'collection_id' column to 'user_vocabulary' table")
        return True
        
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = add_collection_id_column()
    if success:
        print("Database update completed successfully.")
    else:
        print("Database update failed.") 