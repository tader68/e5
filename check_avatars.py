import sqlite3
import os

# Connect to the database
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()

# Get all users with their avatar files
cursor.execute("SELECT id, username, avatar_file FROM user")
users = cursor.fetchall()

# Create avatars directory if it doesn't exist
avatar_dir = 'app/static/uploads/avatars'
if not os.path.exists(avatar_dir):
    os.makedirs(avatar_dir, exist_ok=True)
    print(f"Created avatars directory: {avatar_dir}")

# Check each user's avatar
for user in users:
    user_id, username, avatar_file = user
    
    if not avatar_file or avatar_file == 'default.png':
        print(f"User {username} (ID: {user_id}) uses default avatar")
        continue
    
    # Check if the avatar file exists
    avatar_path = os.path.join(avatar_dir, avatar_file)
    if os.path.exists(avatar_path):
        print(f"User {username} (ID: {user_id}) avatar exists: {avatar_file}")
    else:
        print(f"WARNING: User {username} (ID: {user_id}) avatar missing: {avatar_file}")

# Close the database connection
conn.close() 