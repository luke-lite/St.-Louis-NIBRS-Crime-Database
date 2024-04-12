import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

# Get the length of the table and save it as an integer variable
cursor.execute("SELECT COUNT(*) FROM crime_data")
table_length = cursor.fetchone()[0]

# Get the length of the table by getting the last index value
cursor.execute("SELECT MAX(id) FROM crime_data")
table_length = cursor.fetchone()[0] or 0  # Handle case where table is empty

# Read the CSV file into a DataFrame
new_data = pd.read_csv('new_data.csv')

# 1. Replace old data
for index, row in new_data.iterrows():
    # Check if the 'id' exists in the 'crime_data' table
    cursor.execute("SELECT * FROM crime_data WHERE id=?", (row['id'],))
    existing_row = cursor.fetchone()
    
    if existing_row:
        # If exists, update the row with new data
        cursor.execute("UPDATE crime_data SET column1=?, column2=?, ... WHERE id=?", 
                       (row['column1'], row['column2'], ..., row['id']))

# 2. Add the new data
# Define the specific date from which new data should be added
specific_date = '2024-04-01'  # Change to your specific date

# Filter new data based on the specific date
new_data_after_specific_date = new_data[new_data['date'] > specific_date]

# Append the new data to the 'crime_data' table
new_data_after_specific_date.to_sql('crime_data', conn, if_exists='append', index=False)

# Commit the changes and close connection
conn.commit()
conn.close()