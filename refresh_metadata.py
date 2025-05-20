from app import db, create_app

# Create the application instance
app = create_app()

# Use the application context
with app.app_context():
    # Force SQLAlchemy to refresh its metadata
    db.metadata.clear()
    db.reflect()
    
    print("SQLAlchemy metadata refreshed successfully.") 