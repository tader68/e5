# LingoBoost Language Learning Application

LingoBoost is an AI-powered language learning application designed to help users improve their English language skills through vocabulary flashcards, grammar lessons, reading exercises, and writing tasks.

## Features

- Vocabulary learning with spaced repetition
- Grammar lessons with interactive exercises
- Reading practice with comprehension questions
- Writing tasks with AI-powered feedback
- Achievement system to track progress
- Leaderboards and gamification elements

## Recent Fixes

### Fix for Collection ID Column Error (2025-05-14)

We resolved an issue where the application was encountering a database error related to the `collection_id` column:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: user_vocabulary.collection_id
```

The fixes included:

1. **Fixed model duplication issue**: Merged duplicate `VocabularyCollection` and `VocabularyCollectionItem` models in `models.py` that were causing conflicts.

2. **Implemented proper SQL handling**: 
   - Used raw SQL queries with `sqlalchemy.text()` to bypass ORM issues
   - Modified queries in `check_user_achievements`, `dashboard`, and `profile` routes

3. **Regenerated database tables**: 
   - Created backup of the database
   - Preserved existing data while rebuilding table structures
   - Ensured consistent schema between models and database

These changes allow the application to properly handle the vocabulary collections feature, which organizes words into groups for better learning efficiency.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the environment variables in `.env`
4. Initialize the database: `python create_db.py`
5. Run the application: `python -m flask run`

## Technologies Used

- Flask (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- Google Gemini API (AI features)
- Bootstrap (Frontend)

## Features

- **Vocabulary Speed Learning**: Flashcards, contextual practice, and spaced repetition system
- **Grammar Mastery**: Interactive lessons and diverse exercises
- **Advanced Writing Practice**: AI-powered writing feedback and analysis
- **Smart Reading Comprehension**: Level-appropriate reading materials with auto-generated questions
- **Personal Dashboard**: Track progress and receive personalized learning recommendations
- **Offline Fallback Mode**: The app now includes a fallback mode that works without an API key

## Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **AI Integration**: Google Gemini API for natural language processing
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Authentication**: Flask-Login for user management
- **Database**: SQLite (development), PostgreSQL (production)

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Google Gemini API key (optional, but recommended for full functionality)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/lingoboost-ai.git
   cd lingoboost-ai
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # Optional - for production
   # DATABASE_URL=postgresql://username:password@localhost/lingoboost
   ```

   Note: If you don't provide a valid Gemini API key, the app will run in fallback mode with limited functionality.

5. Initialize the database:
   ```
   flask db-init
   ```

6. Run the application:
   ```
   flask run
   ```

7. Access the application at `http://localhost:5000`

## Fallback Mode

LingoBoost AI now includes a fallback mode that works without a Google Gemini API key. This allows you to:

- Use predefined vocabulary lists for common topics
- Practice with basic exercises
- Experience the UI and flow of the application

To get the full AI-powered experience with personalized content, you'll need to:

1. Get a Google Gemini API key from https://makersuite.google.com/app/apikey
2. Add it to your `.env` file or set it as an environment variable
3. Restart the application

## API Documentation

LingoBoost offers a REST API for integrating AI language learning features into other applications.

### Authentication

All API endpoints require authentication except for the test endpoint.

### Endpoints

#### Test API Connection

```
GET /api/test
```

Response:
```json
{
  "status": "success",
  "message": "LingoBoost AI API is operational",
  "version": "1.0.0"
}
```

#### Generate Vocabulary

```
POST /api/vocabulary/generate
```

Request body:
```json
{
  "topic": "Travel",
  "level": "B1",
  "count": 10
}
```

Response:
```json
{
  "status": "success",
  "data": [
    {
      "word": "destination",
      "type": "noun",
      "phonetics": "/ˌdestɪˈneɪʃn/",
      "meaning": "A place to which someone or something is going or being sent",
      "example": "The Caribbean is a popular tourist destination."
    },
    // More words...
  ]
}
```

## Development Guidelines

### Project Structure

- `app/` - Main application package
  - `auth/` - Authentication module
  - `vocabulary/` - Vocabulary learning module
  - `grammar/` - Grammar learning module
  - `writing/` - Writing practice and feedback module
  - `reading/` - Reading practice module
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `models.py` - Database models
  - `forms.py` - WTForms definitions
  - `gemini_api.py` - Google Gemini API integration

### Adding New Features

1. Create appropriate models in `models.py`
2. Add forms in `forms.py` if needed
3. Add API integration in `gemini_api.py` if needed
4. Create routes in the relevant module
5. Create templates in the corresponding templates directory

### Running Tests

```
pytest
```

## Deployment

### Docker

A Dockerfile is provided for containerization. Build and run with:

```
docker build -t lingoboost .
docker run -p 5000:5000 lingoboost
```

### Heroku

```
heroku create
git push heroku main
heroku config:set SECRET_KEY=your_secret_key_here
heroku config:set GOOGLE_API_KEY=your_gemini_api_key_here
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Gemini API for powering the AI features
- Flask and its ecosystem for providing a robust web framework
- Bootstrap for the responsive UI design

### Change Tracking & Backup Features

The application now includes a comprehensive set of features for tracking changes and maintaining code and database backups:

1. **Automatic Code Backups**
   - Creates ZIP archives of the codebase automatically
   - Backups are stored in `instance/backups/`
   - Database backups are stored as `.bak` files
   - Automatically runs at application startup

2. **Database Schema Versioning**
   - Tracks all database schema changes
   - Captures detailed table and column information
   - Allows restoring to previous schema versions
   - Version history stored in `instance/db_versions/`

3. **File Change Tracking**
   - Monitors all file creations, modifications, and deletions
   - Records changes with timestamps and file hashes
   - Change history stored in `instance/changes/file_changes.json`
   - Logs available in `instance/logs/file_changes.log`

4. **Database Event Logging**
   - Records all database operations (inserts, updates, deletes)
   - Captures before/after values of all modified fields
   - Detailed logging of SQL operations and transaction times
   - Logs stored in `instance/logs/db_events.log` and `instance/db_logs/db_operations.json`

### Using the Change Tracking Features

#### CLI Commands

The following Flask CLI commands are available:

```
flask backup             # Create a manual backup of the code and database
flask db-snapshot        # Create a manual snapshot of the database schema
```

#### Viewing Logs and History

- Code changes: `instance/changes/file_changes.json`
- Database operations: `instance/db_logs/db_operations.json`
- Database versions: `instance/db_versions/version_history.json`
- Log files: `instance/logs/`

### Default Setup

Change tracking is automatically integrated into the application. No additional setup is required.

### Requirements

All necessary packages are listed in `requirements.txt`. The following packages are required for change tracking:

- watchdog==3.0.0

Install dependencies using:

```
pip install -r requirements.txt
```