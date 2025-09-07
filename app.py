from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from database import get_db_connection, init_database
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database on startup
init_database()

# API Routes

@app.route('/api/colleges', methods=['POST'])
def create_college():
    """Create a new college"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'College name is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO colleges (name, location) VALUES (?, ?)",
                  (data['name'], data.get('location', '')))
    college_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'message': 'College created successfully', 'id': college_id}), 201

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student"""
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'email', 'college_id']):
        return jsonify({'error': 'Name, email, and college_id are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO students (name, email, college_id) VALUES (?, ?, ?)",
                      (data['name'], data['email'], data['college_id']))
        student_id = cursor.lastrowid
        conn.commit()
        return jsonify({'message': 'Student created successfully', 'id': student_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    finally:
        conn.close()

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    data = request.get_json()
    required_fields = ['title', 'event_type', 'event_date', 'college_id']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Title, event_type, event_date, and college_id are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (title, description, event_type, event_date, college_id, capacity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['title'], data.get('description', ''), data['event_type'],
          data['event_date'], data['college_id'], data.get('capacity', 100)))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'message': 'Event created successfully', 'id': event_id}), 201

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filtering"""
    college_id = request.args.get('college_id')
    event_type = request.args.get('event_type')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT e.*, c.name as college_name,
               COUNT(r.id) as registrations_count
        FROM events e
        LEFT JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
    """

    conditions = []
    params = []

    if college_id:
        conditions.append("e.college_id = ?")
        params.append(college_id)

    if event_type:
        conditions.append("e.event_type = ?")
        params.append(event_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY e.id ORDER BY e.event_date"

    cursor.execute(query, params)
    events = cursor.fetchall()
    conn.close()

    return jsonify([dict(event) for event in events])

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
def register_student(event_id):
    """Register a student for an event"""
    data = request.get_json()
    if not data or 'student_id' not in data:
        return jsonify({'error': 'Student ID is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if event exists and has capacity
    cursor.execute("""
        SELECT e.capacity, COUNT(r.id) as current_registrations
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        WHERE e.id = ?
        GROUP BY e.id
    """, (event_id,))

    event_data = cursor.fetchone()
    if not event_data:
        conn.close()
        return jsonify({'error': 'Event not found'}), 404

    if event_data['current_registrations'] >= event_data['capacity']:
        conn.close()
        return jsonify({'error': 'Event is at full capacity'}), 400

    # Check if student is already registered
    cursor.execute("SELECT id FROM registrations WHERE student_id = ? AND event_id = ?",
                  (data['student_id'], event_id))

    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Student already registered for this event'}), 400

    # Register the student
    cursor.execute("INSERT INTO registrations (student_id, event_id) VALUES (?, ?)",
                  (data['student_id'], event_id))
    registration_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'message': 'Student registered successfully', 'registration_id': registration_id}), 201

@app.route('/api/attendance/<int:registration_id>', methods=['POST'])
def mark_attendance(registration_id):
    """Mark attendance for a registration"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if registration exists
    cursor.execute("SELECT id FROM registrations WHERE id = ?", (registration_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Registration not found'}), 404

    # Check if attendance already marked
    cursor.execute("SELECT id FROM attendance WHERE registration_id = ?", (registration_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Attendance already marked'}), 400

    # Mark attendance
    cursor.execute("INSERT INTO attendance (registration_id) VALUES (?)", (registration_id,))
    attendance_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'message': 'Attendance marked successfully', 'attendance_id': attendance_id}), 201

@app.route('/api/feedback/<int:registration_id>', methods=['POST'])
def submit_feedback(registration_id):
    """Submit feedback for a registration"""
    data = request.get_json()
    if not data or 'rating' not in data:
        return jsonify({'error': 'Rating is required'}), 400

    rating = data['rating']
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if registration exists
    cursor.execute("SELECT id FROM registrations WHERE id = ?", (registration_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Registration not found'}), 404

    # Check if feedback already submitted
    cursor.execute("SELECT id FROM feedback WHERE registration_id = ?", (registration_id,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Feedback already submitted'}), 400

    # Submit feedback
    cursor.execute("INSERT INTO feedback (registration_id, rating, comments) VALUES (?, ?, ?)",
                  (registration_id, rating, data.get('comments', '')))
    feedback_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'message': 'Feedback submitted successfully', 'feedback_id': feedback_id}), 201

@app.route('/api/reports/events', methods=['GET'])
def event_popularity_report():
    """Get event popularity report sorted by registrations"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.title, e.event_type, e.event_date, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(a.id) as total_attendance,
               ROUND(AVG(f.rating), 2) as avg_rating
        FROM events e
        LEFT JOIN colleges c ON e.college_id = c.id
        LEFT JOIN registrations r ON e.id = r.event_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY e.id
        ORDER BY total_registrations DESC
    """)

    events = cursor.fetchall()
    conn.close()

    return jsonify([dict(event) for event in events])

@app.route('/api/reports/students', methods=['GET'])
def student_participation_report():
    """Get student participation report"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(a.id) as total_attendance,
               ROUND(AVG(f.rating), 2) as avg_rating
        FROM students s
        LEFT JOIN colleges c ON s.college_id = c.id
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY s.id
        ORDER BY total_registrations DESC
    """)

    students = cursor.fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])

@app.route('/api/reports/top-students', methods=['GET'])
def top_students_report():
    """Get top 3 most active students"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.name, s.email, c.name as college_name,
               COUNT(r.id) as total_registrations,
               COUNT(a.id) as total_attendance,
               ROUND(AVG(f.rating), 2) as avg_rating
        FROM students s
        LEFT JOIN colleges c ON s.college_id = c.id
        LEFT JOIN registrations r ON s.id = r.student_id
        LEFT JOIN attendance a ON r.id = a.registration_id
        LEFT JOIN feedback f ON r.id = f.registration_id
        GROUP BY s.id
        ORDER BY total_registrations DESC
        LIMIT 3
    """)

    students = cursor.fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])

# Web Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin portal"""
    return render_template('admin.html')

@app.route('/student')
def student():
    """Student portal"""
    return render_template('student.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
