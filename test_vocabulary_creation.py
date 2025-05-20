from app import create_app, db
from app.models import User, VocabularyWord, UserVocabulary, VocabularyCollection
from datetime import datetime, timedelta

def test_create_vocabulary():
    """Test creating UserVocabulary with all fields"""
    app = create_app()
    
    with app.app_context():
        # Get first user (should be admin or create one)
        user = User.query.first()
        if not user:
            print("No users found in database")
            return False
        
        # Get or create vocabulary word
        word = VocabularyWord.query.first()
        if not word:
            word = VocabularyWord(
                word="test",
                word_type="noun",
                phonetics="/test/",
                meaning="A test word",
                example="This is a test word.",
                level="A1",
                topic="Test"
            )
            db.session.add(word)
            db.session.commit()
            print(f"Created test word with ID: {word.id}")
        
        # Get or create collection
        collection = VocabularyCollection.query.filter_by(user_id=user.id).first()
        if not collection:
            collection = VocabularyCollection(
                user_id=user.id,
                name="Test Collection",
                topic="Test",
                level="A1",
                description="A test collection"
            )
            db.session.add(collection)
            db.session.commit()
            print(f"Created test collection with ID: {collection.id}")
        
        # Create UserVocabulary entry with all fields
        now = datetime.utcnow()
        user_vocabulary = UserVocabulary(
            user_id=user.id,
            word_id=word.id,
            status="learning",
            familiarity_level=0,
            next_review=now + timedelta(days=1),
            last_practiced=now,
            collection_id=collection.id,
            created_at=now,
            review_count=0,
            mastery_level=0
        )
        
        try:
            db.session.add(user_vocabulary)
            db.session.commit()
            print(f"Successfully created UserVocabulary entry with ID: {user_vocabulary.id}")
            
            # Verify entry was created with all fields
            entry = UserVocabulary.query.get(user_vocabulary.id)
            
            # Print all attributes
            print("\nVerifying created entry has all fields:")
            
            # Get all column names
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user_vocabulary')]
            
            # Print values for each column
            for col in columns:
                value = getattr(entry, col, None)
                print(f"- {col}: {value}")
            
            return True
        
        except Exception as e:
            db.session.rollback()
            print(f"Error creating UserVocabulary: {e}")
            return False

if __name__ == "__main__":
    test_create_vocabulary() 