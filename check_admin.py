import sqlite3

conn = sqlite3.connect('lingoboost.db')
cursor = conn.cursor()

# Check if admin user exists
cursor.execute("SELECT username, email, password_note FROM user WHERE username='admin'")
result = cursor.fetchall()

print("Admin user details:", result)

conn.close() 