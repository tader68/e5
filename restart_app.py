"""
Instructions for restarting the Flask application:

1. If you're running the app in development mode with Flask's built-in server:
   - Press Ctrl+C in the terminal where the app is running
   - Run the app again with: python app.py or flask run

2. If you're using a production server like gunicorn:
   - Find the process ID: ps aux | grep gunicorn
   - Send a HUP signal: kill -HUP <process_id>

3. For Windows IIS or other setups:
   - Simply touch the app.py file to trigger a reload

Changes we've made:
1. Added the extras column to the vocabulary_word table
2. Modified the study_flashcards function to handle missing extras fields
3. Initialized null extras values in the database

These changes should fix the flashcard feature and allow collocations and synonyms/antonyms to be stored and displayed correctly.
"""

print("=== LingoBoost Application Restart Instructions ===")
print("")
print("To restart your Flask application and apply changes:")
print("1. Press Ctrl+C in the terminal where the app is running")
print("2. Then run: python app.py")
print("")
print("Your changes have been applied to:")
print("- The database schema (extras column)")
print("- The routes.py file (study_flashcards function)")
print("- All vocabulary words now have initialized extras fields")
print("")
print("The flashcard feature should now work correctly!") 