import os
import sqlite3
import sys
from datetime import datetime

# Database file path
DB_PATH = 'lingoboost.db'

def backup_database():
    """Create a backup of the database before making changes"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{DB_PATH}.bak.{timestamp}"
    
    try:
        with open(DB_PATH, 'rb') as src_file:
            with open(backup_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
        print(f"Database backup created at {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating database backup: {str(e)}")
        return False

def update_user_vocabulary_table():
    """Add the collection_id column to the user_vocabulary table if missing"""
    conn = None
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Connected to database")
        
        # Check if collection_id column exists
        cursor.execute("PRAGMA table_info(user_vocabulary)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns in user_vocabulary: {column_names}")
        
        if 'collection_id' not in column_names:
            print("Collection_id column is missing. Adding it now...")
            
            # Add column to the table
            cursor.execute("ALTER TABLE user_vocabulary ADD COLUMN collection_id INTEGER")
            
            # Add foreign key constraint
            # Note: SQLite doesn't support adding constraints to existing tables directly,
            # so we need to recreate the table with the constraint
            
            # First get the current table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_vocabulary'")
            create_stmt = cursor.fetchone()[0]
            print(f"Current table schema: {create_stmt}")
            
            # Store all current data
            cursor.execute("SELECT * FROM user_vocabulary")
            rows = cursor.fetchall()
            print(f"Found {len(rows)} rows in user_vocabulary table")
            
            # Get column names and types for better debugging
            cursor.execute("PRAGMA table_info(user_vocabulary)")
            columns_info = cursor.fetchall()
            column_details = [(col[1], col[2]) for col in columns_info]
            print(f"Columns with types: {column_details}")
            
            # Recreate the table with the new schema
            print("Recreating table with proper foreign key constraint...")
            cursor.execute("DROP TABLE IF EXISTS user_vocabulary_old")
            cursor.execute("ALTER TABLE user_vocabulary RENAME TO user_vocabulary_old")
            
            # Create the new table with the collection_id foreign key
            cursor.execute("""
            CREATE TABLE user_vocabulary (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                word_id INTEGER,
                status VARCHAR(20),
                familiarity_level INTEGER,
                next_review DATETIME,
                last_practiced DATETIME,
                collection_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(word_id) REFERENCES vocabulary_word(id),
                FOREIGN KEY(collection_id) REFERENCES vocabulary_collection(id)
            )
            """)
            
            # Verify vocabulary_collection table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_collection'")
            if not cursor.fetchone():
                print("Creating vocabulary_collection table...")
                cursor.execute("""
                CREATE TABLE vocabulary_collection (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    description VARCHAR(500),
                    user_id INTEGER,
                    created_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
                """)
                print("vocabulary_collection table created")
            else:
                print("vocabulary_collection table already exists")
            
            # Verify vocabulary_collection_item table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_collection_item'")
            if not cursor.fetchone():
                print("Creating vocabulary_collection_item table...")
                cursor.execute("""
                CREATE TABLE vocabulary_collection_item (
                    id INTEGER PRIMARY KEY,
                    collection_id INTEGER,
                    word_id INTEGER,
                    added_at DATETIME,
                    FOREIGN KEY(collection_id) REFERENCES vocabulary_collection(id),
                    FOREIGN KEY(word_id) REFERENCES vocabulary_word(id)
                )
                """)
                print("vocabulary_collection_item table created")
            else:
                print("vocabulary_collection_item table already exists")
            
            # Copy data from old table to new one
            print(f"Copying {len(rows)} rows of data from old table...")
            
            # Get column info from old table
            cursor.execute("PRAGMA table_info(user_vocabulary_old)")
            old_columns = cursor.fetchall()
            print(f"Old table columns: {old_columns}")
            
            col_count = len(old_columns)
            print(f"Column count: {col_count}")
            
            # Create placeholders for the INSERT statement based on column count
            placeholders = ','.join(['?' for _ in range(col_count)])
            insert_query = f"INSERT INTO user_vocabulary VALUES ({placeholders},NULL)"  # NULL for collection_id
            print(f"Insert query: {insert_query}")
            
            inserted = 0
            for row in rows:
                try:
                    cursor.execute(insert_query, row)
                    inserted += 1
                    if inserted % 100 == 0:
                        print(f"Inserted {inserted} rows...")
                except Exception as e:
                    print(f"Error inserting row {row}: {str(e)}")
            
            print(f"Inserted {inserted} rows out of {len(rows)}")
            
            print("Verifying data...")
            cursor.execute("SELECT COUNT(*) FROM user_vocabulary")
            new_count = cursor.fetchone()[0]
            print(f"New table has {new_count} rows")
            
            # Drop old table if everything is OK
            if new_count == len(rows):
                cursor.execute("DROP TABLE user_vocabulary_old")
                print("Old table dropped successfully")
            else:
                print("WARNING: Row count mismatch! Old table preserved as user_vocabulary_old")
            
            # Commit changes
            conn.commit()
            print("Database update completed successfully!")
        else:
            print("Collection_id column already exists. No changes needed.")
    
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            print("Database connection closed")
    
    return True

if __name__ == "__main__":
    print("LingoBoost - Update User Vocabulary Table Structure")
    print("====================================================")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file {DB_PATH} not found.")
        sys.exit(1)
    else:
        print(f"Database file {DB_PATH} found")
    
    # Create backup before proceeding
    if not backup_database():
        print("Failed to create backup. Aborting.")
        sys.exit(1)
    
    # Update the table structure
    if update_user_vocabulary_table():
        print("Update completed successfully!")
    else:
        print("Update failed!")
    
    print("Script execution finished.") 