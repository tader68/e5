from app import db, create_app
from app.models import VocabularyWord
import json

# Create the application instance
app = create_app()

# Use the application context
with app.app_context():
    print("Checking and fixing extras field in vocabulary_word table...")
    
    # Get all vocabulary words
    words = VocabularyWord.query.all()
    fixed_count = 0
    
    for word in words:
        if word.extras is None:
            # Initialize the extras field with an empty structure
            word.extras = json.dumps({
                'collocations': [],
                'synonyms_antonyms': {
                    'synonyms': [],
                    'antonyms': []
                }
            })
            fixed_count += 1
    
    # Commit changes
    if fixed_count > 0:
        db.session.commit()
        print(f"Fixed {fixed_count} words with null extras field.")
    else:
        print("No words needed fixing.")
    
    print("Done!") 