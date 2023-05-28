import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('C:/Users/user/Documents/GitHub/accessflaskproject/users.db')
cursor = conn.cursor()

# Execute a query to retrieve the table names from sqlite_master table
cursor.execute("SELECT * FROM visitors")

# Fetch all rows from the query result
rows = cursor.fetchall()

column_names = [description[0] for description in cursor.description]

df = pd.DataFrame(rows, columns=column_names)
# Close the cursor and database connection
print(df)

visitors_details = 'visitors_details.xlsx'
df.to_excel(visitors_details, index=False)
print("Saved as successfully:", visitors_details)

cursor.close()
conn.close()
