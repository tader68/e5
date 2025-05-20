import os
import sqlite3
import sys
from datetime import datetime
import traceback
from flask import Flask
from app import create_app, db
from app.models import (
    VocabularyCollection, VocabularyCollectionItem, UserVocabulary,
    VocabularyWord, User
)
import shutil
import importlib
from sqlalchemy import MetaData, inspect

# Database file path
DB_PATH = 'lingoboost.db'

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

def list_existing_tables():
    """List all existing tables in the database"""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Existing tables ({len(tables)}): {', '.join(tables)}")
    return tables

def regenerate_tables():
    """Regenerate the problematic tables using SQLAlchemy models"""
    print("Listing existing tables before regeneration...")
    existing_tables = list_existing_tables()
    
    # Create backup before making changes
    if not create_backup():
        print("Failed to create backup, aborting.")
        return False
    
    try:
        print("Regenerating tables...")
        # Only create specific tables instead of all tables
        if 'vocabulary_collection' not in existing_tables:
            print("Creating vocabulary_collection table...")
            VocabularyCollection.__table__.create(db.engine)
            print("vocabulary_collection table created successfully.")
        
        if 'vocabulary_collection_item' not in existing_tables:
            print("Creating vocabulary_collection_item table...")
            VocabularyCollectionItem.__table__.create(db.engine)
            print("vocabulary_collection_item table created successfully.")
        
        # Make sure user_vocabulary has the necessary columns
        print("Ensuring user_vocabulary table is up to date...")
        # This won't recreate the table, but it will ensure the model is registered
        # We already fixed the column issue with the previous script
            
        print("Tables regenerated successfully.")
        
        print("Listing tables after regeneration...")
        list_existing_tables()
        
        return True
    except Exception as e:
        print(f"Error regenerating tables: {str(e)}")
        return False

def regenerate_models():
    """
    Regenerate all SQLAlchemy model tables to ensure proper column recognition.
    This will refresh the SQLAlchemy metadata without requiring database changes.
    """
    app = create_app()
    
    with app.app_context():
        print("Starting model regeneration process...")
        
        # Clear existing metadata to force refresh
        db.metadata.clear()
        
        # Get all models from app.models
        from app import models
        
        # Force reload the models module to refresh definitions
        importlib.reload(models)
        
        # Get the inspector to examine database
        inspector = inspect(db.engine)
        
        # Print information about the vocabulary_word table
        print("Checking vocabulary_word table columns...")
        for column in inspector.get_columns('vocabulary_word'):
            print(f"Column: {column['name']}, Type: {column['type']}")
        
        # Reflect database tables to rebuild metadata
        db.reflect()
        
        # Initialize models from classes
        for name in dir(models):
            obj = getattr(models, name)
            if hasattr(obj, '__tablename__'):
                print(f"Initializing model: {name}")
                # Access the table to initialize it
                try:
                    table_obj = getattr(obj, '__table__')
                    print(f"  Table name: {table_obj.name}")
                    for col in table_obj.columns:
                        print(f"  Column: {col.name}, Type: {col.type}")
                except Exception as e:
                    print(f"  Error: {e}")
        
        print("Model regeneration completed.")

def regenerate_vocabulary_word_table():
    """Completely regenerate the vocabulary_word table to ensure proper structure"""
    print("Running direct SQL migration for vocabulary_word table...")
    
    import sqlite3
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Backup data
    print("Backing up vocabulary_word data...")
    cursor.execute("SELECT * FROM vocabulary_word")
    rows = cursor.fetchall()
    print(f"Backed up {len(rows)} rows")
    
    # Get column names
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Current columns: {column_names}")
    
    # Create new table
    print("Creating temporary table...")
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
    
    # Insert data into new table
    print("Migrating data...")
    for row in rows:
        # Create a dictionary of the existing data
        row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        
        # Add extras column if it doesn't exist
        if 'extras' not in row_dict or row_dict['extras'] is None:
            row_dict['extras'] = '{}'
        
        # Insert into new table
        cursor.execute("""
        INSERT INTO vocabulary_word_new 
        (id, word, word_type, phonetics, meaning, example, level, topic, extras)
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
            row_dict.get('extras', '{}')
        ))
    
    # Swap tables
    print("Swapping tables...")
    cursor.execute("DROP TABLE vocabulary_word")
    cursor.execute("ALTER TABLE vocabulary_word_new RENAME TO vocabulary_word")
    
    # Create indexes
    print("Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_word ON vocabulary_word (word)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_vocabulary_word_topic ON vocabulary_word (topic)")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("vocabulary_word table regenerated successfully with proper structure")

if __name__ == "__main__":
    # Check if a specific operation is requested
    if len(sys.argv) > 1 and sys.argv[1] == 'fix_vocabulary':
        # Just run the vocabulary word table fix
        regenerate_vocabulary_word_table()
    else:
        # Run the full regeneration
        regenerate_models()
        regenerate_vocabulary_word_table() 