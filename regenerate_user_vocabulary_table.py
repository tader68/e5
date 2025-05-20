import sqlite3
import os
from datetime import datetime
import sys
from app import create_app, db
from app.models import UserVocabulary
from sqlalchemy import inspect

def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"lingoboost.db.bak.{timestamp}"
    
    if os.path.exists('lingoboost.db'):
        import shutil
        shutil.copy2('lingoboost.db', backup_file)
        print(f"Created database backup: {backup_file}")
        return True
    return False

def extract_data():
    """Extract current data from user_vocabulary table"""
    print("Extracting existing data from user_vocabulary table...")
    
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Get columns
    cursor.execute("PRAGMA table_info(user_vocabulary)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"Columns found: {columns}")
    
    # Get data
    cursor.execute("SELECT * FROM user_vocabulary")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} rows of data")
    
    conn.close()
    
    return columns, rows

def drop_and_recreate_table():
    """Drop and recreate user_vocabulary table using SQLAlchemy"""
    print("Initializing app context...")
    app = create_app()
    
    with app.app_context():
        print("Dropping and recreating user_vocabulary table...")
        
        # Drop the table if it exists
        inspector = inspect(db.engine)
        if inspector.has_table('user_vocabulary'):
            db.session.execute(db.text('DROP TABLE IF EXISTS user_vocabulary'))
            db.session.commit()
            print("Dropped existing user_vocabulary table")
        
        # Create the table directly with SQL to ensure all columns are created
        print("Creating user_vocabulary table with SQL")
        
        sql = """
        CREATE TABLE user_vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word_id INTEGER,
            status VARCHAR(20) DEFAULT 'learning',
            familiarity_level INTEGER DEFAULT 0,
            next_review DATETIME,
            last_practiced DATETIME,
            collection_id INTEGER,
            created_at TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES user(id),
            FOREIGN KEY(word_id) REFERENCES vocabulary_word(id),
            FOREIGN KEY(collection_id) REFERENCES vocabulary_collection(id)
        )
        """
        
        db.session.execute(db.text(sql))
        db.session.commit()
        
        # Verify the table structure
        inspector = inspect(db.engine)
        columns = inspector.get_columns('user_vocabulary')
        column_names = [col['name'] for col in columns]
        
        print("\nRecreated table columns:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
        
        # Verify all columns exist
        required_columns = ['id', 'user_id', 'word_id', 'status', 'familiarity_level', 
                          'next_review', 'last_practiced', 'collection_id',
                          'created_at', 'review_count', 'mastery_level']
        
        missing = [col for col in required_columns if col not in column_names]
        
        if missing:
            print(f"\nWARNING: Still missing columns: {missing}")
            return False
        
        print("\nTable successfully recreated with all required columns!")
        return True

def restore_data(columns, rows):
    """Restore data to the recreated table"""
    if not rows:
        print("No data to restore")
        return
    
    print(f"Restoring {len(rows)} rows of data...")
    
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Map old columns to new schema
    new_columns = ['id', 'user_id', 'word_id', 'status', 'familiarity_level', 
                 'next_review', 'last_practiced', 'collection_id',
                 'created_at', 'review_count', 'mastery_level']
    
    column_mapping = {col: idx for idx, col in enumerate(columns) if col in new_columns}
    
    # Prepare for batch insert
    for row in rows:
        # Create a new row with values in the right places
        values = [None] * len(new_columns)
        
        # Map values from old columns to new positions
        for new_idx, new_col in enumerate(new_columns):
            if new_col in column_mapping:
                old_idx = column_mapping[new_col]
                if old_idx < len(row):
                    values[new_idx] = row[old_idx]
        
        # Fill in default values for missing columns
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Make sure required fields have values
        if values[0] is None:  # id - should not happen
            continue  # Skip this row if no ID
            
        if values[1] is None or values[2] is None:  # user_id or word_id
            continue  # Skip this row if no user_id or word_id
            
        if values[8] is None:  # created_at
            values[8] = now
        if values[6] is None:  # last_practiced
            values[6] = now
        if values[5] is None:  # next_review
            values[5] = now
        if values[9] is None:  # review_count
            values[9] = 0
        if values[10] is None:  # mastery_level
            values[10] = 0
        if values[3] is None:  # status
            values[3] = 'learning'
        if values[4] is None:  # familiarity_level
            values[4] = 0
        
        # Create SQL statement
        columns_str = ", ".join(new_columns)
        placeholders = ", ".join(["?"] * len(new_columns))
        
        try:
            cursor.execute(f"INSERT INTO user_vocabulary ({columns_str}) VALUES ({placeholders})", values)
        except Exception as e:
            print(f"Error inserting row {row[0]}: {e}")
    
    conn.commit()
    conn.close()
    print("Data restoration completed!")

if __name__ == '__main__':
    print("Starting complete regeneration of user_vocabulary table...")
    
    # Backup the database
    if not backup_database():
        print("Error: Could not back up the database. Aborting.")
        sys.exit(1)
    
    try:
        # Extract existing data
        columns, rows = extract_data()
        
        # Drop and recreate the table
        if drop_and_recreate_table():
            # Restore data
            restore_data(columns, rows)
            print("\nSuccess! The user_vocabulary table has been regenerated with the correct schema.")
        else:
            print("\nWarning: Table recreation had issues.")
            
    except Exception as e:
        print(f"Error during process: {e}")
        print("Please restore from the backup if needed.") 