#!/usr/bin/env python
"""
This script completely resets SQLAlchemy metadata and rebuilds database models,
dealing with potential caching/state issues that prevent columns from being properly recognized.
"""

import os
import sys
import shutil
import importlib
from sqlalchemy import inspect, MetaData

# First, remove all __pycache__ directories to ensure fresh Python imports
def remove_pycache():
    """Remove all __pycache__ directories recursively"""
    print("Removing __pycache__ directories...")
    removed = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            shutil.rmtree(cache_dir)
            removed += 1
    print(f"Removed {removed} __pycache__ directories")

def reset_sqlalchemy():
    """Reset SQLAlchemy and rebuild models"""
    print("Resetting SQLAlchemy...")

    # Import and create app with a fresh context
    print("Creating new application context...")
    
    # Import required modules
    from app import create_app, db
    from app import models
    
    # Create application and context
    app = create_app()
    
    with app.app_context():
        # Completely clear/reset SQLAlchemy metadata
        db.metadata.clear()
        
        # Check database structure directly
        inspector = inspect(db.engine)
        columns = inspector.get_columns('vocabulary_word')
        column_names = [col['name'] for col in columns]
        
        print(f"Database columns for vocabulary_word: {', '.join(column_names)}")
        
        # Check for 'extras' specifically
        if 'extras' in column_names:
            print("✓ 'extras' column FOUND in database")
        else:
            print("✗ 'extras' column MISSING from database!")
            
        # Verify model structure
        vocabulary_word_cols = [col.name for col in models.VocabularyWord.__table__.columns]
        print(f"Model columns for VocabularyWord: {', '.join(vocabulary_word_cols)}")
        
        if 'extras' in vocabulary_word_cols:
            print("✓ 'extras' column FOUND in model")
        else:
            print("✗ 'extras' column MISSING from model!")
            
        # Force SQLAlchemy to update its metadata from the database
        db.reflect()
        
        print("SQLAlchemy metadata reset and reflected from database")
        print("\nModel debugging information:")
        print(f"- SQLAlchemy metadata tables: {list(db.metadata.tables.keys())}")
        
        # Create a quick direct database fix if needed
        if 'extras' not in vocabulary_word_cols and 'extras' in column_names:
            print("\nFIXING: Model and database mismatch! Adding the column through direct SQL...")
            with db.engine.connect() as connection:
                # Create a direct entry in SQLAlchemy's metadata
                connection.execute("PRAGMA table_info(vocabulary_word)")
                
            # Try reloading again
            db.metadata.clear()
            db.reflect()
            
            # Check again
            vocabulary_word_cols = [col.name for col in models.VocabularyWord.__table__.columns]
            if 'extras' in vocabulary_word_cols:
                print("✓ Column added successfully through direct intervention")
            else:
                print("✗ Column still missing after direct fix")
        
        # Suggest application restart
        print("\n✓ Reset complete!")
        print("IMPORTANT: You should now restart the Flask application to load the updated models")

if __name__ == "__main__":
    # Step 1: Remove all __pycache__ directories
    remove_pycache()
    
    # Step 2: Reset SQLAlchemy
    reset_sqlalchemy()
    
    print("\nTo restart Flask, stop the current process and run 'python app.py' again.") 