from app import db, create_app
import importlib
from sqlalchemy import inspect

def fix_sqlalchemy_models():
    """
    Fix SQLAlchemy models to ensure proper column recognition,
    particularly for the extras column in vocabulary_word table.
    """
    app = create_app()
    
    with app.app_context():
        print("Starting SQLAlchemy model fix process...")
        
        # Clear existing metadata cache
        db.metadata.clear()
        
        # Get all models from app.models
        from app import models
        
        # Force reload the models module to refresh definitions
        importlib.reload(models)
        
        # Get the inspector to examine database
        inspector = inspect(db.engine)
        
        # Print information about the vocabulary_word table
        print("Checking vocabulary_word table columns...")
        for column in inspector.get_columns('vocabulary_word'):
            print(f"Column: {column['name']}, Type: {column['type']}")
        
        # Access the VocabularyWord model specifically
        vocabulary_word = models.VocabularyWord
        
        # Print the model's __table__ columns
        print("\nChecking VocabularyWord model columns...")
        for column in vocabulary_word.__table__.columns:
            print(f"Column: {column.name}, Type: {column.type}")
            
        # Ensure 'extras' column is recognized
        if hasattr(vocabulary_word, 'extras'):
            print("'extras' attribute exists in the model")
        else:
            print("ERROR: 'extras' attribute missing from the model")
            
        # Force SQLAlchemy to rebuild table metadata
        db.reflect()
        
        print("Model fix completed. Try using the application now.")

if __name__ == "__main__":
    fix_sqlalchemy_models() 