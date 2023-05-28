import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('C:/Users/user/Documents/GitHub/accessflaskproject/users.db')
cursor = conn.cursor()

# Execute a query to retrieve the table names from sqlite_master table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

# Fetch all rows from the query result
tables = cursor.fetchall()

# Iterate over the table names
for table in tables:
    table_name = table[0]
    print("Table:", table_name)

    # Execute a query to fetch all records from the current table
    query = "SELECT * FROM {}".format(table_name)
    cursor.execute(query)
    rows = cursor.fetchall()

    # Get the column names from the table
    cursor.execute("PRAGMA table_info({})".format(table_name))
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Convert the retrieved data to a Pandas DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    print("Data:")
    print(df)
    print()

    # Save the DataFrame to an Excel file
    all_data = "{}.xlsx".format(table_name)
    df.to_excel(all_data, index=False)
    print("Saved as:", all_data)

# Close the cursor and database connection
cursor.close()
conn.close()
