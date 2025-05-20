import sqlite3
import os

print("Setting admin avatar...")

# Check available avatar files
avatar_dir = 'app/static/uploads/avatars'
if os.path.exists(avatar_dir):
    files = os.listdir(avatar_dir)
    print(f"Available avatar files: {files}")
else:
    print(f"Avatar directory {avatar_dir} doesn't exist!")
    exit(1)

# Connect to the database
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()

# Set admin avatar to the found PNG file or default.png
admin_avatar = '49071dafe5334263b82308029d871d92.png' if '49071dafe5334263b82308029d871d92.png' in files else 'default.png'
print(f"Setting admin avatar to: {admin_avatar}")

cursor.execute("UPDATE user SET avatar_file = ? WHERE username = 'admin'", (admin_avatar,))
conn.commit()
print(f"Updated admin avatar in database")

# Verify the change
cursor.execute("SELECT username, avatar_file FROM user WHERE username = 'admin'")
admin = cursor.fetchone()
if admin:
    print(f"Admin user: {admin[0]}, Avatar file: {admin[1]}")
else:
    print("Admin user not found")

# Close the connection
conn.close()
print("Completed") 