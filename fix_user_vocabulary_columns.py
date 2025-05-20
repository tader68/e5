import sqlite3
import os
from datetime import datetime

def add_missing_columns():
    """Add missing columns to the user_vocabulary table"""
    print("Adding missing columns to user_vocabulary table...")
    
    # Connect to the database
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(user_vocabulary)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add created_at column if it doesn't exist
    if 'created_at' not in columns:
        print("Adding created_at column")
        cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN created_at TIMESTAMP")
        # Initialize with current timestamp for existing records
        cursor.execute("UPDATE user_vocabulary SET created_at = ?", (datetime.utcnow(),))
    
    # Add review_count column if it doesn't exist
    if 'review_count' not in columns:
        print("Adding review_count column")
        cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN review_count INTEGER DEFAULT 0")
    
    # Add mastery_level column if it doesn't exist
    if 'mastery_level' not in columns:
        print("Adding mastery_level column")
        cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN mastery_level INTEGER DEFAULT 0")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    # Create a backup of the database before making changes
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"lingoboost.db.bak.{timestamp}"
    
    if os.path.exists('lingoboost.db'):
        import shutil
        shutil.copy2('lingoboost.db', backup_file)
        print(f"Created database backup: {backup_file}")
    
    add_missing_columns() 