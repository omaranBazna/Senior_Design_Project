CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    pre_requisite TEXT,
    course_name TEXT,
    section TEXT,
    credits TEXT,
    instructor TEXT,
    times TEXT,
    campus TEXT,
    remaining_seats TEXT
);