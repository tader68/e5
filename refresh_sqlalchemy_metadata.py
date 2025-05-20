#!/usr/bin/env python
"""
This script refreshes SQLAlchemy metadata to ensure it correctly recognizes all columns,
particularly the 'extras' column in the vocabulary_word table.
"""

import os
import sys
import importlib
from sqlalchemy import MetaData, Table, Column, Text

def clear_python_cache():
    """Clear all Python cache files"""
    print("Clearing Python cache...")
    
    # Count of removed files/dirs
    removed = 0
    
    # Remove all __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            try:
                import shutil
                shutil.rmtree(pycache_dir)
                removed += 1
                print(f"Removed: {pycache_dir}")
            except Exception as e:
                print(f"Error removing {pycache_dir}: {e}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                try:
                    os.remove(pyc_file)
                    removed += 1
                except Exception as e:
                    print(f"Error removing {pyc_file}: {e}")
    
    print(f"✓ Removed {removed} cache files/directories")

def refresh_metadata():
    """Refresh SQLAlchemy metadata"""
    print("Refreshing SQLAlchemy metadata...")
    
    # Import the app with a fresh import
    if 'app' in sys.modules:
        del sys.modules['app']
    if 'app.models' in sys.modules:
        del sys.modules['app.models']
        
    from app import create_app, db
    
    app = create_app()
    
    with app.app_context():
        # Clear existing metadata
        print("Clearing existing metadata...")
        db.metadata.clear()
        
        # Import models to get class definitions
        from app import models
        
        # Check VocabularyWord model
        vocabulary_word = models.VocabularyWord
        
        # Get table info from database
        inspector = db.inspect(db.engine)
        
        # Check vocabulary_word table columns in database
        print("\nChecking database columns for vocabulary_word table:")
        db_columns = inspector.get_columns('vocabulary_word')
        db_column_names = [col['name'] for col in db_columns]
        
        for i, col in enumerate(db_columns):
            print(f"  {i+1}. {col['name']} ({col['type']})")
        
        # Verify extras column in database
        if 'extras' in db_column_names:
            print("\n✓ 'extras' column exists in the database")
        else:
            print("\n✗ 'extras' column is MISSING from the database")
            
        # Check model definition
        print("\nChecking model columns for VocabularyWord:")
        model_columns = vocabulary_word.__table__.columns
        model_column_names = [col.name for col in model_columns]
        
        for i, col in enumerate(model_columns):
            print(f"  {i+1}. {col.name} ({col.type})")
            
        # Verify extras column in model
        if 'extras' in model_column_names:
            print("\n✓ 'extras' column exists in the model")
        else:
            print("\n✗ 'extras' column is MISSING from the model")
            
        # Force SQLAlchemy to reflect the database
        print("\nForcing SQLAlchemy to reflect database tables...")
        db.reflect()
        
        # Reload the models module to pick up changes
        importlib.reload(models)
        
        # Check model again after reflect
        print("\nChecking model columns after reflection:")
        model_columns = [col.name for col in models.VocabularyWord.__table__.columns]
        print(f"  Columns: {', '.join(model_columns)}")
        
        if 'extras' in model_columns:
            print("✓ 'extras' column exists in the model after reflection")
        else:
            # If still missing, try direct modification
            print("✗ 'extras' column still missing after reflection")
            print("\nAttempting direct model metadata modification...")
            
            # Clear metadata again
            db.metadata.clear()
            
            # Explicitly redefine the table to include the extras column
            Table('vocabulary_word', db.metadata, autoload_with=db.engine)
            
            # Check metadata after direct modification
            vocabulary_word_table = db.metadata.tables['vocabulary_word']
            if 'extras' in vocabulary_word_table.columns:
                print("✓ Fixed through direct metadata modification")
            else:
                print("✗ Could not fix through direct modification")
                
        print("\nMetadata refresh completed")

if __name__ == "__main__":
    # Clear Python cache first
    clear_python_cache()
    
    # Refresh SQLAlchemy metadata
    refresh_metadata()
    
    print("\nIMPORTANT: Please restart the Flask application to apply the changes") 