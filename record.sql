CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    course_name TEXT,
    pre_requisite TEXT,
    attribute TEXT ,
    credits TEXT,
    section TEXT,
    times TEXT
);