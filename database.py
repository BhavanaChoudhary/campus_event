import sqlite3
from datetime import datetime

def get_db_connection():
    """Create and return database connection"""
    conn = sqlite3.connect('campus_events.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create colleges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            college_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (college_id) REFERENCES colleges (id)
        )
    ''')

    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT NOT NULL,
            event_date DATE NOT NULL,
            college_id INTEGER,
            capacity INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (college_id) REFERENCES colleges (id)
        )
    ''')

    # Create registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (event_id) REFERENCES events (id),
            UNIQUE(student_id, event_id)
        )
    ''')

    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER,
            checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (registration_id) REFERENCES registrations (id),
            UNIQUE(registration_id)
        )
    ''')

    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comments TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (registration_id) REFERENCES registrations (id),
            UNIQUE(registration_id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_sample_data():
    """Insert sample data for testing"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert sample college
    cursor.execute("INSERT OR IGNORE INTO colleges (name, location) VALUES (?, ?)",
                  ("Sample University", "City Center"))

    # Insert sample students
    students = [
        ("John Doe", "john.doe@university.edu", 1),
        ("Jane Smith", "jane.smith@university.edu", 1),
        ("Bob Johnson", "bob.johnson@university.edu", 1),
        ("Alice Brown", "alice.brown@university.edu", 1),
        ("Charlie Wilson", "charlie.wilson@university.edu", 1)
    ]

    for student in students:
        cursor.execute("INSERT OR IGNORE INTO students (name, email, college_id) VALUES (?, ?, ?)", student)

    # Insert sample events
    events = [
        ("Tech Workshop", "Learn about latest technologies", "Workshop", "2024-12-15", 1, 50),
        ("Hackathon 2024", "48-hour coding competition", "Hackathon", "2024-12-20", 1, 100),
        ("AI Seminar", "Introduction to Artificial Intelligence", "Seminar", "2024-12-25", 1, 75),
        ("Career Fair", "Meet potential employers", "Fest", "2025-01-10", 1, 200),
        ("Web Development Bootcamp", "Hands-on web development", "Workshop", "2025-01-15", 1, 30)
    ]

    for event in events:
        cursor.execute("INSERT OR IGNORE INTO events (title, description, event_type, event_date, college_id, capacity) VALUES (?, ?, ?, ?, ?, ?)", event)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    insert_sample_data()
    print("Database initialized with sample data!")
