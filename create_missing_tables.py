from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect
import os
from datetime import datetime
import shutil
from app import create_app, db
from app.models import DeletedVocabularyWord

# Create a minimal Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lingoboost.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def create_backup():
    """Create a backup of the database before making changes"""
    database_path = 'lingoboost.db'
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{database_path}.bak.{timestamp}"
    
    try:
        shutil.copy2(database_path, backup_filename)
        print(f"Created backup: {backup_filename}")
        return True
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    exists = table_name in tables
    if exists:
        print(f"Table '{table_name}' already exists in the database.")
    else:
        print(f"Table '{table_name}' does NOT exist in the database.")
    return exists

def create_vocabulary_collection_table():
    """Create the vocabulary_collection table if it doesn't exist"""
    if check_table_exists('vocabulary_collection'):
        return True
        
    try:
        db.session.execute(text("""
        CREATE TABLE vocabulary_collection (
            id INTEGER NOT NULL, 
            user_id INTEGER, 
            name VARCHAR(200), 
            topic VARCHAR(100), 
            level VARCHAR(10), 
            created_at DATETIME, 
            description TEXT, 
            PRIMARY KEY (id), 
            FOREIGN KEY(user_id) REFERENCES user (id)
        )
        """))
        db.session.commit()
        print("Successfully created vocabulary_collection table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating vocabulary_collection table: {str(e)}")
        return False

def create_vocabulary_collection_item_table():
    """Create the vocabulary_collection_item table if it doesn't exist"""
    if check_table_exists('vocabulary_collection_item'):
        return True
        
    try:
        db.session.execute(text("""
        CREATE TABLE vocabulary_collection_item (
            id INTEGER NOT NULL, 
            collection_id INTEGER, 
            word_id INTEGER, 
            added_at DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(collection_id) REFERENCES vocabulary_collection (id), 
            FOREIGN KEY(word_id) REFERENCES vocabulary_word (id)
        )
        """))
        db.session.commit()
        print("Successfully created vocabulary_collection_item table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating vocabulary_collection_item table: {str(e)}")
        return False

def create_deleted_vocabulary_word_table():
    """Create the deleted_vocabulary_word table if it doesn't exist"""
    if check_table_exists('deleted_vocabulary_word'):
        return True
        
    try:
        db.session.execute(text("""
        CREATE TABLE deleted_vocabulary_word (
            id INTEGER NOT NULL,
            original_id INTEGER,
            word VARCHAR(100) NOT NULL,
            word_type VARCHAR(50),
            meaning TEXT,
            example TEXT,
            phonetics VARCHAR(100),
            level VARCHAR(5),
            topic VARCHAR(50),
            deleted_at DATETIME,
            deleted_by VARCHAR(100),
            PRIMARY KEY (id)
        )
        """))
        db.session.commit()
        print("Successfully created deleted_vocabulary_word table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating deleted_vocabulary_word table: {str(e)}")
        return False

def create_deleted_vocabulary_image_cache_table():
    """Create the deleted_vocabulary_image_cache table if it doesn't exist"""
    if check_table_exists('deleted_vocabulary_image_cache'):
        return True
        
    try:
        db.session.execute(text("""
        CREATE TABLE deleted_vocabulary_image_cache (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            word_type TEXT,
            topic TEXT,
            image_url TEXT NOT NULL,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_by TEXT
        )
        """))
        db.session.commit()
        print("Successfully created deleted_vocabulary_image_cache table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating deleted_vocabulary_image_cache table: {str(e)}")
        return False

def fix_tables():
    """Create all the missing tables"""
    # First create a backup
    if not create_backup():
        print("Failed to create backup, aborting.")
        return False
        
    success = True
    
    # Create vocabulary_collection table
    if not create_vocabulary_collection_table():
        success = False
        
    # Create vocabulary_collection_item table
    if not create_vocabulary_collection_item_table():
        success = False
    
    # Create deleted_vocabulary_word table
    if not create_deleted_vocabulary_word_table():
        success = False
    
    # Create deleted_vocabulary_image_cache table
    if not create_deleted_vocabulary_image_cache_table():
        success = False
        
    return success

if __name__ == "__main__":
    with app.app_context():
        print("Checking for missing tables in the database...")
        if fix_tables():
            print("Database update completed successfully.")
            
            # Double check for deleted_vocabulary_word table
            print("\nFinal check for deleted_vocabulary_word table:")
            check_table_exists('deleted_vocabulary_word')
        else:
            print("Database update encountered errors.") 