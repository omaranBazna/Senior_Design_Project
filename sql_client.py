import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)

def InsertToSQL(data):
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table

    #['ACC 4510', 'Auditing', "['Accounting 3120,D', 'and', 'Mathematics 2140,D', 'or', 'Statistics 2250,D']", '3', 'Tuesday-Thursday , 02:00 PM - 03:15 PM', '']
    insert_query = '''
        INSERT INTO courses (course_code, course_name, pre_requisite,section,credits,times,attribute)
        VALUES (?, ?, ?, ?,?,?,?)
    '''
  
    print(data[0])

    #cursor.execute("delete from courses where id > 0 ")
    # Insert the data into the table

    cursor.executemany(insert_query, data)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Data inserted successfully.")


def InsertElementToSQL(element):
    print("Insert:")
    print(element)
    print(len(element))

    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file
    check_element  = find_element_section(element[0],element[3])
    print(check_element)
    print("-----------")
    if len(check_element) > 0: 
        print("duplicated element")
        return None
    # Create a cursor object
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO courses (course_code, course_name, pre_requisite,section,credits,times,attribute)
        VALUES (?, ?, ?, ?,?,?,?)
    '''

    cursor.execute(insert_query, element)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Data inserted successfully.")


def find_element(element):
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    select_query = '''
        select * from courses where course_code = ?
    '''
    cursor.execute(select_query, (element,))  # Replace with your data
    data = cursor.fetchall()
    # Close the connection
    conn.close()

    return data

def find_element_by_attr_only(attribute):
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    select_query = '''
        select * from courses where attribute LIKE '%'''+attribute+'''%'
    '''

    cursor.execute(select_query)  # Replace with your data
    data = cursor.fetchall()
    print(data)
    # Close the connection
    conn.close()

    return data


def get_attr_list_elements():
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    select_query = '''
    SELECT TRIM(attribute) AS trimmed_attribute
    FROM courses
    WHERE TRIM(attribute) != '';
    '''
    cursor.execute(select_query)  # Replace with your data
    data = cursor.fetchall()
    # Close the connection
    conn.close()

    return data

def find_element_section(element,section):
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    select_query = '''
        select * from courses where course_code = ? and section = ?
    '''
    cursor.execute(select_query, (element,section))  # Replace with your data
    data = cursor.fetchall()
    # Close the connection
    conn.close()

    return data


def get_all_elements():
    database_str = "C:\omaran\SeniorDesignProject\database_2.db"
    conn = sqlite3.connect(database_str)  # Replace with your database file

    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to insert data into the 'courses' table
    select_query = '''
        select * from courses
    '''
    cursor.execute(select_query)  # Replace with your data

    data = cursor.fetchall()
    # Close the connection
    conn.close()

    return data



