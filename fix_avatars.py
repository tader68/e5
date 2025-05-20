import sqlite3
import os
import shutil

print("Starting avatar fix script...")

# Connect to the database
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()
print("Connected to database")

# Create avatars directory if it doesn't exist
avatar_dir = 'app/static/uploads/avatars'
if not os.path.exists(avatar_dir):
    os.makedirs(avatar_dir, exist_ok=True)
    print(f"Created avatars directory: {avatar_dir}")
else:
    print(f"Avatars directory exists: {avatar_dir}")

# Ensure default.png exists in the avatars directory
default_avatar = os.path.join(avatar_dir, 'default.png')
if not os.path.exists(default_avatar):
    # Create a default avatar by copying an existing image or creating one
    # For this example, we'll just create a small text file as a placeholder
    with open(default_avatar, 'w') as f:
        f.write("This is a placeholder for the default avatar image")
    print(f"Created placeholder default avatar at {default_avatar}")

# Get all users with their avatar files
cursor.execute("SELECT id, username, avatar_file FROM user")
users = cursor.fetchall()
print(f"Found {len(users)} users in database")

# Fix each user's avatar if needed
for user in users:
    user_id, username, avatar_file = user
    
    # If no avatar or the file doesn't exist, reset to default
    if not avatar_file or avatar_file == 'None' or avatar_file == 'default.png':
        print(f"Setting default avatar for user {username} (ID: {user_id})")
        cursor.execute("UPDATE user SET avatar_file = 'default.png' WHERE id = ?", (user_id,))
    else:
        avatar_path = os.path.join(avatar_dir, avatar_file)
        if not os.path.exists(avatar_path):
            print(f"Avatar file missing for {username}: {avatar_file}, resetting to default")
            cursor.execute("UPDATE user SET avatar_file = 'default.png' WHERE id = ?", (user_id,))
        else:
            print(f"User {username} avatar exists: {avatar_file}")

# Commit changes
conn.commit()
print("Database changes committed")

# Close the database connection
conn.close()
print("Avatar fix complete")