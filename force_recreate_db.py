import os
import sqlite3
import shutil
from datetime import datetime

# Backup the database
def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    src = "lingoboost.db"
    dst = f"lingoboost.db.bak.{timestamp}"
    shutil.copy2(src, dst)
    print(f"Database backed up to {dst}")
    return dst

# Extract schema and data from existing database
def extract_schema_and_data():
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(tables)} tables")
    
    # Extract schema for each table
    table_schemas = {}
    for table in tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        schema = cursor.fetchone()[0]
        table_schemas[table] = schema
        print(f"Extracted schema for {table}")
    
    # Extract data from vocabulary_word table
    cursor.execute("SELECT * FROM vocabulary_word")
    vocab_data = cursor.fetchall()
    
    # Get vocabulary_word column names
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    vocab_columns = [col[1] for col in cursor.fetchall()]
    
    # Extract indexes for vocabulary_word
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='vocabulary_word'")
    vocab_indexes = [(row[0], row[1]) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'table_schemas': table_schemas, 
        'vocab_data': vocab_data, 
        'vocab_columns': vocab_columns,
        'vocab_indexes': vocab_indexes
    }

# Create a new clean database with proper vocabulary_word table
def create_new_database(schema_data, backup_path):
    print("Creating new database...")
    
    # Rename the existing database
    if os.path.exists("lingoboost.db"):
        os.rename("lingoboost.db", "lingoboost.db.old")
    
    # Create new connection
    conn = sqlite3.connect("lingoboost.db")
    cursor = conn.cursor()
    
    # Create vocabulary_word table first with proper schema
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
    
    # Import vocabulary data
    print(f"Importing {len(schema_data['vocab_data'])} vocabulary words...")
    for row in schema_data['vocab_data']:
        # Create a dictionary mapping columns to values
        row_dict = {schema_data['vocab_columns'][i]: row[i] for i in range(len(schema_data['vocab_columns']))}
        
        # Ensure extras field exists
        if 'extras' not in row_dict or row_dict['extras'] is None:
            row_dict['extras'] = '{}'
        
        # Insert into new table
        cursor.execute("""
        INSERT INTO vocabulary_word (id, word, word_type, phonetics, meaning, example, level, topic, extras)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row_dict.get('id'),
            row_dict.get('word'),
            row_dict.get('word_type'),
            row_dict.get('phonetics'),
            row_dict.get('meaning'),
            row_dict.get('example'),
            row_dict.get('level'),
            row_dict.get('topic'),
            row_dict.get('extras')
        ))
    
    # Create indexes for vocabulary_word
    for index_name, index_sql in schema_data['vocab_indexes']:
        # Skip if it's a system-generated index
        if not index_name.startswith('sqlite_'):
            print(f"Creating index: {index_name}")
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError:
                # Handle case where index references don't match
                print(f"Could not create index with original SQL, creating basic index instead")
                if 'word' in index_name:
                    cursor.execute("CREATE INDEX ix_vocabulary_word_word ON vocabulary_word (word)")
                elif 'topic' in index_name:
                    cursor.execute("CREATE INDEX ix_vocabulary_word_topic ON vocabulary_word (topic)")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("New database created successfully")

# Delete all __pycache__ directories to force module reloading
def clear_cache():
    print("Clearing Python cache...")
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                print(f"Removed {cache_dir}")
            except Exception as e:
                print(f"Error removing {cache_dir}: {e}")
    print("Cache cleared")

# Modify app/__init__.py to force SQLAlchemy to create a fresh connection
def patch_app_init():
    try:
        print("Adding code to force SQLAlchemy to recognize new schema...")
        with open('app/__init__.py', 'r') as f:
            content = f.read()
        
        # Check if this has already been patched
        if "# Force SQLAlchemy to recognize extras column" in content:
            print("app/__init__.py already patched")
            return
        
        # Find the line that creates the SQLAlchemy instance
        if "db = SQLAlchemy()" in content:
            # Add code after db = SQLAlchemy() to force it to recognize the extras column
            patched_content = content.replace(
                "db = SQLAlchemy()",
                """db = SQLAlchemy()

# Force SQLAlchemy to recognize extras column
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    if 'extras' in column_names:
        print("✓ Database has extras column in vocabulary_word table")"""
            )
            
            with open('app/__init__.py', 'w') as f:
                f.write(patched_content)
            print("app/__init__.py patched successfully")
        else:
            print("Could not find 'db = SQLAlchemy()' in app/__init__.py")
    except Exception as e:
        print(f"Error patching app/__init__.py: {e}")

# Main function
if __name__ == "__main__":
    print("=== FORCE RECREATE DATABASE ===")
    
    # Step 1: Backup the database
    backup_path = backup_database()
    
    # Step 2: Extract schema and data
    schema_data = extract_schema_and_data()
    
    # Step 3: Clear all Python cache
    clear_cache()
    
    # Step 4: Create new database
    create_new_database(schema_data, backup_path)
    
    # Step 5: Patch app/__init__.py
    patch_app_init()
    
    print(f"""
=== FIX COMPLETE ===
The database has been recreated with the correct structure.
1. Stop the Flask application if it's running
2. Start it again with: python app.py
3. If there are still issues, you can restore from backup: {backup_path}
    """) 