import sqlite3


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect("student_registration.db")
cursor = conn.cursor()


# ============================================================
# CREATE TABLES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    schedule TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    student_id TEXT,
    course_code TEXT,
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_code) REFERENCES courses(course_code)
)
""")

conn.commit()


# ============================================================
# INSERT SAMPLE COURSES
# ============================================================

sample_courses = [
    (
        "CSE101",
        "Python Programming",
        "Introduction to Python programming",
        30,
        "Monday 10:00 AM - 12:00 PM"
    ),
    (
        "ECE201",
        "Digital Electronics",
        "Fundamentals of digital electronic circuits",
        25,
        "Tuesday 10:00 AM - 12:00 PM"
    ),
    (
        "DBMS301",
        "Database Management System",
        "Database concepts, SQL and DBMS",
        35,
        "Wednesday 2:00 PM - 4:00 PM"
    ),
    (
        "ECE302",
        "Fiber Optics",
        "Fundamentals and applications of optical fiber",
        20,
        "Thursday 10:00 AM - 12:00 PM"
    ),
    (
        "MAT101",
        "Engineering Mathematics",
        "Mathematics for engineering students",
        40,
        "Friday 9:00 AM - 11:00 AM"
    )
]

for course in sample_courses:
    cursor.execute("""
    INSERT OR IGNORE INTO courses
    (course_code, title, description, capacity, schedule)
    VALUES (?, ?, ?, ?, ?)
    """, course)

conn.commit()


# ============================================================
# ADD STUDENT
# ============================================================

def add_student():
    print("\n========== STUDENT REGISTRATION ==========")

    student_id = input("Enter Student ID: ").strip()
    name = input("Enter Student Name: ").strip()

    if student_id == "" or name == "":
        print("\nStudent ID and name cannot be empty.")
        return

    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )

    existing_student = cursor.fetchone()

    if existing_student:
        print("\nStudent already exists.")
    else:
        cursor.execute(
            "INSERT INTO students (student_id, name) VALUES (?, ?)",
            (student_id, name)
        )
        conn.commit()

        print("\nStudent added successfully!")


# ============================================================
# DISPLAY COURSES
# ============================================================

def display_courses():
    print("\n================ AVAILABLE COURSES ================")

    cursor.execute("""
    SELECT
        c.course_code,
        c.title,
        c.description,
        c.capacity,
        c.schedule,
        COUNT(r.student_id) AS registered
    FROM courses c
    LEFT JOIN registrations r
    ON c.course_code = r.course_code
    GROUP BY c.course_code
    """)

    courses = cursor.fetchall()

    if not courses:
        print("No courses available.")
        return

    for course in courses:
        code, title, description, capacity, schedule, registered = course

        available = capacity - registered

        print("\n-----------------------------------------------")
        print("Course Code :", code)
        print("Title       :", title)
        print("Description :", description)
        print("Capacity    :", capacity)
        print("Registered  :", registered)
        print("Available   :", available)
        print("Schedule    :", schedule)

    print("-----------------------------------------------")


# ============================================================
# REGISTER FOR COURSE
# ============================================================

def register_course():
    print("\n========== REGISTER FOR COURSE ==========")

    student_id = input("Enter Student ID: ").strip()

    # Check student
    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        print("\nStudent not found.")
        print("Please register the student first.")
        return

    display_courses()

    course_code = input("\nEnter Course Code: ").strip().upper()

    # Check course
    cursor.execute(
        "SELECT * FROM courses WHERE course_code = ?",
        (course_code,)
    )

    course = cursor.fetchone()

    if course is None:
        print("\nCourse not found.")
        return

    # Check duplicate registration
    cursor.execute("""
    SELECT * FROM registrations
    WHERE student_id = ? AND course_code = ?
    """, (student_id, course_code))

    already_registered = cursor.fetchone()

    if already_registered:
        print("\nYou are already registered for this course.")
        return

    # Check capacity
    cursor.execute("""
    SELECT COUNT(*)
    FROM registrations
    WHERE course_code = ?
    """, (course_code,))

    registered_count = cursor.fetchone()[0]

    capacity = course[3]

    if registered_count >= capacity:
        print("\nSorry! This course is full.")
        return

    # Register student
    cursor.execute("""
    INSERT INTO registrations
    (student_id, course_code)
    VALUES (?, ?)
    """, (student_id, course_code))

    conn.commit()

    print("\nCourse registration successful!")
    print("Student :", student[1])
    print("Course  :", course[1])


# ============================================================
# DROP COURSE
# ============================================================

def drop_course():
    print("\n========== DROP COURSE ==========")

    student_id = input("Enter Student ID: ").strip()

    # Check student
    cursor.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:
        print("\nStudent not found.")
        return

    # Display student's courses
    view_registered_courses(student_id)

    course_code = input(
        "\nEnter Course Code to drop: "
    ).strip().upper()

    # Check registration
    cursor.execute("""
    SELECT *
    FROM registrations
    WHERE student_id = ? AND course_code = ?
    """, (student_id, course_code))

    registration = cursor.fetchone()

    if registration is None:
        print("\nYou are not registered for this course.")
        return

    cursor.execute("""
    DELETE FROM registrations
    WHERE student_id = ? AND course_code = ?
    """, (student_id, course_code))

    conn.commit()

    print("\nCourse dropped successfully!")


# ============================================================
# VIEW REGISTERED COURSES
# ============================================================

def view_registered_courses(student_id=None):
    if student_id is None:
        student_id = input("Enter Student ID: ").strip()

    cursor.execute("""
    SELECT s.name, c.course_code, c.title, c.schedule
    FROM students s
    JOIN registrations r
        ON s.student_id = r.student_id
    JOIN courses c
        ON r.course_code = c.course_code
    WHERE s.student_id = ?
    """, (student_id,))

    courses = cursor.fetchall()

    print("\n========== REGISTERED COURSES ==========")

    if not courses:
        print("No courses registered.")
        return

    print("Student Name:", courses[0][0])

    for course in courses:
        print("-----------------------------------------")
        print("Course Code:", course[1])
        print("Title      :", course[2])
        print("Schedule   :", course[3])

    print("-----------------------------------------")


# ============================================================
# SEARCH COURSE
# ============================================================

def search_course():
    print("\n========== SEARCH COURSE ==========")

    keyword = input("Enter course code or title: ").strip()

    cursor.execute("""
    SELECT course_code, title, description, capacity, schedule
    FROM courses
    WHERE course_code LIKE ?
       OR title LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    courses = cursor.fetchall()

    if not courses:
        print("\nNo matching courses found.")
        return

    for course in courses:
        print("\n-----------------------------------------")
        print("Course Code :", course[0])
        print("Title       :", course[1])
        print("Description :", course[2])
        print("Capacity    :", course[3])
        print("Schedule    :", course[4])


# ============================================================
# DISPLAY STUDENTS
# ============================================================

def display_students():
    print("\n========== STUDENT LIST ==========")

    cursor.execute("""
    SELECT student_id, name
    FROM students
    ORDER BY student_id
    """)

    students = cursor.fetchall()

    if not students:
        print("No students registered.")
        return

    for student in students:
        print("-----------------------------------------")
        print("Student ID :", student[0])
        print("Name       :", student[1])


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():

    while True:

        print("\n")
        print("==============================================")
        print("     STUDENT COURSE REGISTRATION SYSTEM")
        print("==============================================")
        print("1. Add Student")
        print("2. Display Available Courses")
        print("3. Register for Course")
        print("4. Drop Course")
        print("5. View Registered Courses")
        print("6. Search Course")
        print("7. Display Students")
        print("8. Exit")
        print("==============================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student()

        elif choice == "2":
            display_courses()

        elif choice == "3":
            register_course()

        elif choice == "4":
            drop_course()

        elif choice == "5":
            view_registered_courses()

        elif choice == "6":
            search_course()

        elif choice == "7":
            display_students()

        elif choice == "8":
            print("\nThank you for using the Student Course Registration System.")

            conn.close()
            break

        else:
            print("\nInvalid choice. Please enter 1 to 8.")


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main_menu()