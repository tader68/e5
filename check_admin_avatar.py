import sqlite3
import os

print("Starting admin avatar check...")

# Connect to the database
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()
print("Connected to database")

# Check if user table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
if cursor.fetchone():
    print("User table exists")
else:
    print("User table doesn't exist!")
    exit(1)

# Get admin user avatar file
print("Querying for admin user...")
cursor.execute("SELECT id, username, avatar_file FROM user WHERE username = 'admin'")
admin = cursor.fetchone()

print(f"Query result: {admin}")

if admin:
    user_id, username, avatar_file = admin
    print(f"Admin user found: ID={user_id}, Username={username}, Avatar={avatar_file}")
    
    if not avatar_file or avatar_file == 'default.png':
        print("Admin uses default avatar")
    else:
        # Check if the avatar file exists
        avatar_path = os.path.join('app/static/uploads/avatars', avatar_file)
        print(f"Checking if avatar exists at: {avatar_path}")
        if os.path.exists(avatar_path):
            print(f"Admin avatar file exists at: {avatar_path}")
        else:
            print(f"WARNING: Admin avatar file is missing at: {avatar_path}")
            
            # Set the avatar back to default
            cursor.execute("UPDATE user SET avatar_file = 'default.png' WHERE username = 'admin'")
            conn.commit()
            print("Reset admin avatar to default.png")
else:
    print("Admin user not found!")

# Close the database connection
conn.close()
print("Database connection closed") 