import sqlite3

# Connect to the database
conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()

# Query for admin user
cursor.execute("SELECT username, avatar_file FROM user WHERE username = 'admin'")
admin = cursor.fetchone()

if admin:
    print(f"Admin user: {admin[0]}, Avatar file: {admin[1]}")
else:
    print("Admin user not found")

# Close the connection
conn.close() 