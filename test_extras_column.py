#!/usr/bin/env python
"""
Test script to verify if SQLAlchemy correctly recognizes the extras column
"""
import traceback
import sys

print("Starting extras column test...")

try:
    from app import create_app, db
    print("Successfully imported app")
    
    try:
        from app.models import VocabularyWord
        print("Successfully imported VocabularyWord model")
        import json
        
        def test_extras_column():
            """Test if extras column is correctly recognized by SQLAlchemy"""
            try:
                app = create_app()
                print("Successfully created app instance")
                
                with app.app_context():
                    print("=== Testing SQLAlchemy Extras Column Recognition ===")
                    
                    # Check if extras attribute exists in model
                    attrs = dir(VocabularyWord)
                    print(f"VocabularyWord attributes: {', '.join([a for a in attrs if not a.startswith('_')])}")
                    
                    if hasattr(VocabularyWord, 'extras'):
                        print("✓ 'extras' attribute exists in VocabularyWord model")
                        
                        # Check columns in table definition
                        columns = [c.name for c in VocabularyWord.__table__.columns]
                        print(f"Model columns: {', '.join(columns)}")
                        
                        if 'extras' in columns:
                            print("✓ 'extras' column exists in SQLAlchemy table definition")
                        else:
                            print("✗ 'extras' column is missing from SQLAlchemy table definition")
                            return False
                            
                        # Try to create a test word with extras
                        try:
                            test_word = VocabularyWord(
                                word="test_extras",
                                word_type="noun",
                                meaning="A test word for extras column",
                                example="This is a test example.",
                                level="B1",
                                topic="test",
                                extras=json.dumps({"test": True})
                            )
                            
                            # Add to session but don't commit yet
                            db.session.add(test_word)
                            print("✓ Successfully created word with extras")
                            
                            # Try to query with extras filter
                            try:
                                # First rollback to avoid the test word
                                db.session.rollback()
                                
                                # Get one word with extras is not null
                                print("Attempting query with extras filter...")
                                word = VocabularyWord.query.filter(VocabularyWord.extras != None).first()
                                if word:
                                    print(f"✓ Successfully queried with extras filter: {word.word}")
                                    return True
                                else:
                                    print("No words found with non-null extras")
                                    
                                    # Try creating and committing one
                                    test_word = VocabularyWord(
                                        word="test_extras_commit",
                                        word_type="noun",
                                        meaning="A test word for extras column",
                                        example="This is a test example.",
                                        level="B1",
                                        topic="test",
                                        extras=json.dumps({"test": True, "committed": True})
                                    )
                                    print("Created test_word object, about to add to session")
                                    db.session.add(test_word)
                                    print("Added to session, about to commit")
                                    db.session.commit()
                                    print("✓ Created and committed test word with extras")
                                    
                                    # Try querying again
                                    print("Attempting second query with extras filter...")
                                    word = VocabularyWord.query.filter(VocabularyWord.extras != None).first()
                                    if word:
                                        print(f"✓ Successfully queried with extras filter after commit: {word.word}")
                                        
                                        # Clean up test word
                                        db.session.delete(word)
                                        db.session.commit()
                                        print("✓ Cleaned up test word")
                                        return True
                                    else:
                                        print("✗ Failed to query word with extras even after commit")
                                        return False
                            except Exception as e:
                                print(f"✗ Error querying with extras filter: {e}")
                                traceback.print_exc()
                                return False
                        except Exception as e:
                            print(f"✗ Error creating word with extras: {e}")
                            traceback.print_exc()
                            return False
                    else:
                        print("✗ 'extras' attribute is missing from VocabularyWord model")
                        return False
            except Exception as e:
                print(f"✗ Error in test_extras_column: {e}")
                traceback.print_exc()
                return False
        
        print("Defined test function, about to run it")
        success = test_extras_column()
        
        if success:
            print("\n=== TEST PASSED: SQLAlchemy correctly recognizes the extras column ===")
        else:
            print("\n=== TEST FAILED: SQLAlchemy still doesn't recognize the extras column ===")
            print("Try running reset_vocabulary_table.py and clearing all __pycache__ directories again.")
    except Exception as e:
        print(f"Error importing VocabularyWord model: {e}")
        traceback.print_exc()
except Exception as e:
    print(f"Error importing app: {e}")
    traceback.print_exc()

print("Test script completed.") 