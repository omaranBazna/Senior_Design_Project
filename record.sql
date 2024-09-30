CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code INTEGER,
    pre_requisite TEXT,
    course_name TEXT,
    instructor TEXT,
    times TEXT,
    remaining_seats TEXT
);