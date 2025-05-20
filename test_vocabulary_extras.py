#!/usr/bin/env python
"""
This script tests that the 'extras' column in vocabulary_word table
is correctly recognized by SQLAlchemy.
"""

import json
from app import create_app, db
from app.models import VocabularyWord

def test_extras_column():
    """Test the extras column in the VocabularyWord model"""
    print("Testing SQLAlchemy extras column recognition...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        # Check model definition
        print("Checking model definition...")
        vocab_cols = [col.name for col in VocabularyWord.__table__.columns]
        print(f"Model columns: {', '.join(vocab_cols)}")
        
        if 'extras' in vocab_cols:
            print("✓ 'extras' column exists in model definition")
        else:
            print("✗ 'extras' column missing from model definition")
            return False
        
        # Try creating a test word
        print("\nCreating test vocabulary word...")
        try:
            # Create sample extras data
            extras_data = {
                'collocations': ['test collocation 1', 'test collocation 2'],
                'synonyms_antonyms': {
                    'synonyms': ['test synonym 1', 'test synonym 2'],
                    'antonyms': ['test antonym 1', 'test antonym 2']
                }
            }
            
            # Create test word
            test_word = VocabularyWord(
                word='test_extras_column',
                word_type='noun',
                phonetics='/tɛst/',
                meaning='A test word to verify extras column',
                example='This is a test example',
                level='A1',
                topic='test',
                extras=json.dumps(extras_data)
            )
            
            # Add to session
            db.session.add(test_word)
            db.session.commit()
            print(f"✓ Created test word with ID: {test_word.id}")
            
            # Try retrieving the word and checking extras
            retrieved_word = VocabularyWord.query.filter_by(word='test_extras_column').first()
            
            if retrieved_word:
                print(f"✓ Retrieved test word with ID: {retrieved_word.id}")
                
                # Check extras data
                try:
                    extras_json = retrieved_word.extras
                    print(f"✓ Extras data: {extras_json[:100]}...")
                    
                    # Parse JSON
                    parsed_extras = json.loads(extras_json)
                    print("✓ Successfully parsed extras JSON")
                    
                    # Verify content
                    if 'collocations' in parsed_extras and 'synonyms_antonyms' in parsed_extras:
                        print("✓ Extras data structure is correct")
                    else:
                        print("✗ Extras data structure is incorrect")
                        
                except Exception as e:
                    print(f"✗ Error handling extras data: {e}")
                    return False
            else:
                print("✗ Could not retrieve test word")
                return False
                
            # Clean up
            print("\nCleaning up test data...")
            db.session.delete(test_word)
            db.session.commit()
            print("✓ Test data cleaned up")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during test: {e}")
            # Try to rollback any pending changes
            db.session.rollback()
            return False

if __name__ == "__main__":
    # Run the test
    success = test_extras_column()
    
    if success:
        print("\n✅ TEST PASSED: The extras column is working correctly with SQLAlchemy!")
    else:
        print("\n❌ TEST FAILED: There is still an issue with the extras column.") 