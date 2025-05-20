from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import sqlite3

app = create_app()

# First try using SQLAlchemy within the app context
with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(email='admin@lingoboost.com').first()
    
    if admin:
        # Reset password to Admin@123
        admin.password_hash = generate_password_hash('Admin@123')
        admin.password_note = 'Admin@123'  # Update the stored original password
        
        # Save changes
        db.session.commit()
        print("Admin password has been reset to 'Admin@123' using SQLAlchemy")
    else:
        print("Admin account not found using SQLAlchemy, trying direct SQL...")

# If that didn't work, try direct SQL approach
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()

# Update password and password_note
cursor.execute("UPDATE user SET password_hash=?, password_note=? WHERE username=?", 
               (generate_password_hash('Admin@123'), 'Admin@123', 'admin'))

# Commit the changes
conn.commit()

# Verify the change
cursor.execute("SELECT username, email, password_note FROM user WHERE username='admin'")
result = cursor.fetchall()
print("Updated admin details:", result)

conn.close()
print("Admin password has also been reset using direct SQL") 