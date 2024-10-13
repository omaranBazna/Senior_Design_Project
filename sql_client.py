import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)

def InsertToSQL(data):
    database_str = "C:\omaran\SeniorDesignProject\database.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    insert_query = '''
        INSERT INTO courses (course_code, pre_requisite, course_name,section ,
    credits, instructor ,times,campus, remaining_seats)
        VALUES (?, ?, ?, ?, ?, ?,?,?,?)
    '''
    print(data[0])

    cursor.execute("delete from courses where id > 0 ")
    # Insert the data into the table

    cursor.executemany(insert_query, data)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Data inserted successfully.")