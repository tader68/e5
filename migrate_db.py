from app import create_app, db
from app.models import User, League, Achievement, UserLeague
from datetime import datetime, date
import os
import sys
import sqlite3
import shutil

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Created database backup at {backup_path}")
    return backup_path

def add_column_if_not_exists(cursor, table, column, column_type):
    """Add a column to a table if it doesn't exist"""
    # Check if the column exists
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [column_info[1] for column_info in cursor.fetchall()]
    
    if column not in columns:
        print(f"Adding column {column} to {table}")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        return True
    else:
        print(f"Column {column} already exists in {table}")
        return False

def migrate_password_note_field():
    """Add password_note field to User model"""
    try:
        # Check if the column already exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'password_note' not in column_names:
            cursor.execute("ALTER TABLE user ADD COLUMN password_note VARCHAR(128)")
            conn.commit()
            print("Added password_note column to User model")
        else:
            print("password_note column already exists in User model")
    except Exception as e:
        conn.rollback()
        print(f"Error adding password_note column: {str(e)}")

def migrate_league_table():
    """Update the league table and add user leagues"""
    try:
        # Check if the league table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='league'")
        league_table_exists = cursor.fetchone() is not None
        
        if not league_table_exists:
            print("Creating league table...")
            cursor.execute("""
                CREATE TABLE league (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50),
                    rank INTEGER
                )
            """)
            
            # Initialize leagues
            leagues = [
                {'name': 'Bronze', 'rank': 1},
                {'name': 'Silver', 'rank': 2},
                {'name': 'Gold', 'rank': 3},
                {'name': 'Sapphire', 'rank': 4},
                {'name': 'Ruby', 'rank': 5},
                {'name': 'Diamond', 'rank': 6}
            ]
            
            for league_data in leagues:
                cursor.execute(
                    "INSERT INTO league (name, rank) VALUES (?, ?)",
                    (league_data['name'], league_data['rank'])
                )
            
            conn.commit()
            print(f"Added {len(leagues)} leagues")
        else:
            print("League table already exists")
            
        # Check if user_league table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_league'")
        user_league_table_exists = cursor.fetchone() is not None
        
        if not user_league_table_exists:
            print("Creating user_league table...")
            cursor.execute("""
                CREATE TABLE user_league (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    league_id INTEGER,
                    weekly_xp INTEGER DEFAULT 0,
                    weekly_rank INTEGER,
                    week_number INTEGER,
                    joined_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (league_id) REFERENCES league (id)
                )
            """)
            conn.commit()
            print("Created user_league table")
        else:
            print("user_league table already exists")
            
    except Exception as e:
        conn.rollback()
        print(f"Error migrating league tables: {str(e)}")

def migrate_user_avatar_field():
    """Add avatar_file field to User model"""
    try:
        # Check if the column already exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'avatar_file' not in column_names:
            cursor.execute("ALTER TABLE user ADD COLUMN avatar_file VARCHAR(255) DEFAULT 'default.png'")
            conn.commit()
            print("Added avatar_file column to User model")
        else:
            print("avatar_file column already exists in User model")
    except Exception as e:
        conn.rollback()
        print(f"Error adding avatar_file column: {str(e)}")

if __name__ == "__main__":
    # Connect to database
    conn = sqlite3.connect('lingoboost.db')
    
    # Create backup before migration
    backup_database('lingoboost.db')
    
    # Run migrations
    migrate_password_note_field()
    migrate_league_table()
    migrate_user_avatar_field()
    
    # Close connection
    conn.close()
    print("Database migration completed successfully!") 