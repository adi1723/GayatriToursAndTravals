import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')  # Make sure to use your correct file path
cursor = conn.cursor()

# Run the PRAGMA query to check table schema
cursor.execute("PRAGMA table_info(booking);")

# Fetch and print the result
columns = cursor.fetchall()
for column in columns:
    print(column)

# Close the connection
conn.close()
