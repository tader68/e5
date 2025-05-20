from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from datetime import datetime
import shutil

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

def check_column_exists():
    """Check if collection_id column exists in user_vocabulary table"""
    try:
        # Query table information using SQLAlchemy
        result = db.session.execute(
            text("PRAGMA table_info(user_vocabulary)")
        )
        columns = result.fetchall()
        
        column_names = [column[1] for column in columns]
        print(f"Existing columns in user_vocabulary: {column_names}")
        
        if 'collection_id' in column_names:
            print("Column 'collection_id' already exists in user_vocabulary table.")
            return True
        else:
            print("Column 'collection_id' does NOT exist in user_vocabulary table.")
            return False
    except Exception as e:
        print(f"Error checking column existence: {str(e)}")
        return None

def add_collection_id_column():
    """Add collection_id column to user_vocabulary table"""
    try:
        # First check if column already exists
        if check_column_exists():
            return True
            
        # Create backup before modifying
        if not create_backup():
            print("Failed to create backup, aborting.")
            return False
            
        # Add the column
        db.session.execute(
            text("ALTER TABLE user_vocabulary ADD COLUMN collection_id INTEGER REFERENCES vocabulary_collection(id)")
        )
        db.session.commit()
        
        print("Successfully added 'collection_id' column to user_vocabulary table")
        
        # Verify the column was added
        if check_column_exists():
            print("Column addition verified successfully.")
            return True
        else:
            print("Column addition could not be verified!")
            return False
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    with app.app_context():
        print("Checking for missing column in user_vocabulary table...")
        success = add_collection_id_column()
        if success:
            print("Database update completed successfully.")
        else:
            print("Database update failed.") 