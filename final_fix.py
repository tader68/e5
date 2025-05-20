#!/usr/bin/env python
"""
Final fix for the stubborn SQLAlchemy 'extras' column issue.

This script:
1. Creates a database backup
2. Completely recreates the database from scratch
3. Forces SQLAlchemy to refresh its metadata
4. Verifies all columns are properly recognized
"""
import os
import sys
import shutil
import sqlite3
import json
import importlib
from datetime import datetime

print("=== FINAL DATABASE FIX ===")

# Backup the existing database
def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    src = "lingoboost.db"
    dst = f"lingoboost.db.bak.{timestamp}"
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✓ Created database backup: {dst}")
        return True
    else:
        print("! Database file not found, will create new")
        return False

# Clear Python cache to force module reloading
def clear_cache():
    """Clear all Python cache files"""
    print("\n=== Clearing Python Cache ===")
    cache_dirs = []
    
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                cache_path = os.path.join(root, dir)
                cache_dirs.append(cache_path)
                
                # Remove all cache files
                for file in os.listdir(cache_path):
                    try:
                        os.remove(os.path.join(cache_path, file))
                    except Exception as e:
                        print(f"! Error removing {file}: {e}")
    
    print(f"✓ Cleared {len(cache_dirs)} __pycache__ directories")
    
    # Clear modules from sys.modules
    app_modules = [m for m in sys.modules if m.startswith('app')]
    for module in app_modules:
        del sys.modules[module]
    
    print(f"✓ Removed {len(app_modules)} app modules from sys.modules")
    return True

# Create a completely fresh database
def create_fresh_database():
    """Create a completely fresh database with all tables"""
    print("\n=== Creating Fresh Database ===")
    
    # Remove existing database file if it exists
    if os.path.exists("lingoboost.db"):
        try:
            os.remove("lingoboost.db")
            print("✓ Removed existing database file")
        except Exception as e:
            print(f"! Error removing database file: {e}")
            return False
    
    # Now import the app with a fresh import
    try:
        from app import create_app, db
        from app.models import (
            User, VocabularyWord, UserVocabulary, GrammarTopic,
            GrammarProgress, Achievement
        )
        
        app = create_app()
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ Created all database tables")
            
            # Verify the vocabulary_word table has been created with extras column
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if 'vocabulary_word' in inspector.get_table_names():
                columns = inspector.get_columns('vocabulary_word')
                column_names = [col['name'] for col in columns]
                
                print(f"vocabulary_word columns: {', '.join(column_names)}")
                
                if 'extras' in column_names:
                    print("✓ 'extras' column exists in vocabulary_word table")
                else:
                    print("! 'extras' column is missing, adding it...")
                    
                    # Add extras column using raw SQL
                    db.engine.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
                    print("✓ Added extras column using SQL")
            else:
                print("! vocabulary_word table doesn't exist!")
                return False
            
            # Initialize database with a test vocabulary word to verify functionality
            test_word = VocabularyWord(
                word="test_word",
                word_type="noun",
                meaning="A test word to verify database functionality",
                level="B1",
                topic="test",
                extras=json.dumps({"test": True, "created": str(datetime.now())})
            )
            
            db.session.add(test_word)
            db.session.commit()
            print("✓ Added test vocabulary word")
            
            # Try to retrieve the word with extras column
            try:
                word = VocabularyWord.query.filter(VocabularyWord.word == "test_word").first()
                
                if word and hasattr(word, 'extras'):
                    print(f"✓ Successfully retrieved test word with extras: {word.extras}")
                    return True
                else:
                    print("! Could not verify extras column")
                    return False
            except Exception as e:
                print(f"! Error querying test word: {e}")
                return False
    except Exception as e:
        print(f"! Error creating database: {e}")
        return False

# Verify database and SQLAlchemy are in sync
def verify_database():
    """Verify database and SQLAlchemy are in sync"""
    print("\n=== Verifying Database and SQLAlchemy Sync ===")
    
    try:
        from app import create_app, db
        from app.models import VocabularyWord
        from sqlalchemy import inspect
        
        app = create_app()
        
        with app.app_context():
            # Check database columns
            inspector = inspect(db.engine)
            db_columns = inspector.get_columns('vocabulary_word')
            db_column_names = [col['name'] for col in db_columns]
            
            # Check SQLAlchemy model columns
            model_columns = [c.name for c in VocabularyWord.__table__.columns]
            
            print(f"Database columns: {', '.join(db_column_names)}")
            print(f"SQLAlchemy columns: {', '.join(model_columns)}")
            
            # Check if extras column is in both
            if 'extras' in db_column_names and 'extras' in model_columns:
                print("✓ 'extras' column exists in both database and SQLAlchemy model")
                return True
            else:
                if 'extras' not in db_column_names:
                    print("! 'extras' column missing from database")
                if 'extras' not in model_columns:
                    print("! 'extras' column missing from SQLAlchemy model")
                return False
    except Exception as e:
        print(f"! Error verifying database: {e}")
        return False

# Run the complete fix procedure
def run_complete_fix():
    """Run all fix procedures"""
    # Step 1: Backup the database
    backup_database()
    
    # Step 2: Clear Python cache
    clear_cache()
    
    # Step 3: Create fresh database
    if create_fresh_database():
        print("\n✓ Database successfully recreated with extras column")
    else:
        print("\n! Database recreation failed, check error messages above")
        return False
    
    # Step 4: Verify database and SQLAlchemy are in sync
    if verify_database():
        print("\n=== FIX SUCCESSFUL ===")
        print("The 'extras' column is now properly recognized by SQLAlchemy.")
        print("You can now restart your application and it should work correctly.")
    else:
        print("\n=== FIX FAILED ===")
        print("There is still an issue with the 'extras' column.")
        print("Please check your VocabularyWord model definition and database structure.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_complete_fix()
    
    if success:
        print("\nRun your application with: python app.py")
    else:
        print("\nFix failed. Try the following:")
        print("1. Manually remove all __pycache__ directories")
        print("2. Restart your development environment or IDE")
        print("3. Verify app/models.py includes: extras = db.Column(db.Text, nullable=True)")
        print("4. Run this script again") 