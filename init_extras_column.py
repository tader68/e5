from app import create_app, db
import sqlite3
import json

app = create_app()

def init_extras_column():
    """Initialize the extras column in vocabulary_word table if it doesn't exist"""
    print("Checking vocabulary_word table schema...")
    
    # Check if extras column exists
    conn = sqlite3.connect('lingoboost.db')
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(vocabulary_word)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Check if extras column exists
    if 'extras' not in columns:
        print("Adding extras column to vocabulary_word table...")
        cursor.execute("ALTER TABLE vocabulary_word ADD COLUMN extras TEXT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Extras column already exists.")
    
    # Initialize all null extras fields
    print("Initializing null extras fields...")
    cursor.execute("SELECT id FROM vocabulary_word WHERE extras IS NULL")
    null_extras_ids = [row[0] for row in cursor.fetchall()]
    
    if null_extras_ids:
        print(f"Found {len(null_extras_ids)} words with null extras field.")
        
        # Initialize with empty structure
        default_extras = json.dumps({
            'collocations': [],
            'synonyms_antonyms': {
                'synonyms': [],
                'antonyms': []
            }
        })
        
        for word_id in null_extras_ids:
            cursor.execute(
                "UPDATE vocabulary_word SET extras = ? WHERE id = ?",
                (default_extras, word_id)
            )
        
        conn.commit()
        print(f"Successfully initialized {len(null_extras_ids)} words.")
    else:
        print("No null extras fields found.")
    
    # Close connection
    conn.close()
    print("Done!")

# Run the function
if __name__ == "__main__":
    init_extras_column() 