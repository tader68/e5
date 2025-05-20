import sqlite3
import os
from datetime import datetime

def add_missing_last_practiced():
    """Add missing last_practiced column to the user_vocabulary table"""
    print("Adding missing last_practiced column to user_vocabulary table...")
    
    # Connect to the database
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(user_vocabulary)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add last_practiced column if it doesn't exist
    if 'last_practiced' not in columns:
        print("Adding last_practiced column")
        cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN last_practiced TIMESTAMP")
        # Initialize with current timestamp for existing records
        cursor.execute("UPDATE user_vocabulary SET last_practiced = ?", (datetime.utcnow(),))
    else:
        print("last_practiced column already exists")
    
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
    
    add_missing_last_practiced() 