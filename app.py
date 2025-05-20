from app import create_app, db
from app.models import (
    User, VocabularyWord, UserVocabulary, GrammarTopic, GrammarProgress,
    WritingTask, ReadingText, ReadingQuestion, ReadingProgress,
    Achievement, UserAchievement
)
import update_app

app = create_app()
update_app.integrate_change_tracking(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'VocabularyWord': VocabularyWord,
        'UserVocabulary': UserVocabulary,
        'GrammarTopic': GrammarTopic,
        'GrammarProgress': GrammarProgress,
        'WritingTask': WritingTask,
        'ReadingText': ReadingText,
        'ReadingQuestion': ReadingQuestion,
        'ReadingProgress': ReadingProgress,
        'Achievement': Achievement,
        'UserAchievement': UserAchievement
    }

@app.cli.command("db-init")
def init_db():
    """Initialize the database and create all tables"""
    db.create_all()
    print("Database initialized successfully!")

if __name__ == '__main__':
    app.run(debug=True) 