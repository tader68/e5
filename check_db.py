import sqlite3

def check_vocabulary_table():
    """Check the vocabulary_word table structure in detail"""
    try:
        # Connect to the database
        conn = sqlite3.connect('lingoboost.db')
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
        if not cursor.fetchone():
            print("ERROR: vocabulary_word table does not exist!")
            return
            
        # Get the table definition
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='vocabulary_word'")
        table_def = cursor.fetchone()[0]
        print(f"Table definition:\n{table_def}\n")
        
        # Get column information
        cursor.execute("PRAGMA table_info(vocabulary_word)")
        columns = cursor.fetchall()
        print("Column details:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check if extras column exists
        has_extras = any(col[1] == 'extras' for col in columns)
        if has_extras:
            print("\n✓ 'extras' column exists in the database schema")
        else:
            print("\n✗ 'extras' column is MISSING from the database schema")
            
        # Count rows in the table
        cursor.execute("SELECT COUNT(*) FROM vocabulary_word")
        row_count = cursor.fetchone()[0]
        print(f"\nTotal rows in vocabulary_word: {row_count}")
        
        if row_count > 0:
            # Sample some data
            cursor.execute("SELECT * FROM vocabulary_word LIMIT 1")
            sample = cursor.fetchone()
            col_names = [description[0] for description in cursor.description]
            print("\nSample data (first row):")
            for i, name in enumerate(col_names):
                print(f"  {name}: {sample[i]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    print("=== Checking Vocabulary Table Structure ===\n")
    check_vocabulary_table() 