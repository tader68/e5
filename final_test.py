#!/usr/bin/env python
"""
Final test script to verify that the vocabulary_word.extras column issue is fixed.
This script:
1. Creates a fresh database connection
2. Verifies the extras column exists in the database
3. Tests adding and retrieving data with the extras column
"""
import os
import sys
import sqlite3
import json
import traceback

print("=== TESTING VOCABULARY_WORD.EXTRAS COLUMN ===")

# First check database structure directly 
def check_database_structure():
    """Check the database structure directly with SQLite"""
    print("\n1. Checking database structure with SQLite")
    
    try:
        # Connect to the database
        conn = sqlite3.connect("lingoboost.db")
        cursor = conn.cursor()
        
        # Check if vocabulary_word table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
        if not cursor.fetchone():
            print("✗ Error: vocabulary_word table doesn't exist!")
            conn.close()
            return False
        
        # Check column structure
        cursor.execute("PRAGMA table_info(vocabulary_word)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Database columns: {', '.join(column_names)}")
        
        if 'extras' in column_names:
            print("✓ extras column exists in database schema")
            
            # Try to add a test row
            cursor.execute("SELECT COUNT(*) FROM vocabulary_word")
            count = cursor.fetchone()[0]
            print(f"Current vocabulary word count: {count}")
            
            if count == 0:
                print("Adding a test word...")
                test_data = {
                    "collocations": ["test collocation"],
                    "synonyms": ["test synonym"]
                }
                cursor.execute("""
                INSERT INTO vocabulary_word 
                (word, word_type, meaning, level, topic, extras)
                VALUES (?, ?, ?, ?, ?, ?)
                """, ("test_word", "noun", "A test word", "A1", "test", json.dumps(test_data)))
                conn.commit()
                print("✓ Added test word to database")
            
            # Verify we can retrieve it
            cursor.execute("SELECT id, word, extras FROM vocabulary_word LIMIT 1")
            result = cursor.fetchone()
            if result:
                print(f"✓ Retrieved test word: id={result[0]}, word='{result[1]}', extras='{result[2]}'")
            else:
                print("✗ No words found in vocabulary_word table")
            
            conn.close()
            return True
        else:
            print("✗ extras column is missing from database schema")
            conn.close()
            return False
    except Exception as e:
        print(f"✗ Error checking database: {e}")
        traceback.print_exc()
        return False

# Test with SQLAlchemy
def test_with_sqlalchemy():
    """Test accessing the extras column with SQLAlchemy"""
    print("\n2. Testing with SQLAlchemy")
    
    try:
        # Force module reload
        for module in list(sys.modules.keys()):
            if module.startswith('app'):
                del sys.modules[module]
        
        # Import with fresh modules
        from app import create_app, db
        print("✓ Successfully imported app")
        
        from app.models import VocabularyWord
        print("✓ Successfully imported VocabularyWord model")
        
        # Check model definition
        columns = [c.name for c in VocabularyWord.__table__.columns]
        print(f"Model columns: {', '.join(columns)}")
        
        if 'extras' in columns:
            print("✓ extras column exists in SQLAlchemy model")
        else:
            print("✗ extras column is missing from SQLAlchemy model")
            return False
        
        # Create app and test in context
        app = create_app()
        
        with app.app_context():
            print("\nTesting in app context...")
            
            # Test query
            try:
                word = VocabularyWord.query.first()
                if word:
                    print(f"✓ Successfully retrieved word: {word.word}")
                    
                    # Access extras
                    try:
                        extras = word.extras
                        print(f"✓ Successfully accessed extras: {extras}")
                        return True
                    except Exception as e:
                        print(f"✗ Error accessing extras property: {e}")
                        traceback.print_exc()
                        return False
                else:
                    print("No words found, adding a test word...")
                    
                    # Create a test word
                    test_word = VocabularyWord(
                        word="sqlalchemy_test",
                        word_type="noun",
                        meaning="SQLAlchemy test word",
                        level="B1",
                        topic="test",
                        extras=json.dumps({"test": True, "source": "SQLAlchemy"})
                    )
                    
                    # Save it
                    db.session.add(test_word)
                    db.session.commit()
                    print(f"✓ Added test word with ID: {test_word.id}")
                    
                    # Query with extras column
                    try:
                        query_result = VocabularyWord.query.filter(VocabularyWord.extras != None).first()
                        if query_result:
                            print(f"✓ Successfully queried with extras filter: {query_result.word}")
                            print(f"✓ Extras content: {query_result.extras}")
                            return True
                        else:
                            print("✗ No results found when querying with extras filter")
                            return False
                    except Exception as e:
                        print(f"✗ Error querying with extras filter: {e}")
                        traceback.print_exc()
                        return False
            except Exception as e:
                print(f"✗ Error in query: {e}")
                traceback.print_exc()
                return False
    except Exception as e:
        print(f"✗ Error in SQLAlchemy test: {e}")
        traceback.print_exc()
        return False

# Run the tests
db_result = check_database_structure()
sqlalchemy_result = test_with_sqlalchemy()

print("\n=== TEST SUMMARY ===")
print(f"Database structure test: {'PASSED' if db_result else 'FAILED'}")
print(f"SQLAlchemy test: {'PASSED' if sqlalchemy_result else 'FAILED'}")

if db_result and sqlalchemy_result:
    print("\n✅ SUCCESS! The extras column issue has been fixed.")
    print("You can now use your application normally.")
else:
    print("\n❌ ISSUES REMAIN. The extras column is not fully fixed.")
    print("Review the errors above for more details.") 