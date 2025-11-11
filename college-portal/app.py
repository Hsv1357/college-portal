from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, date
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATABASE = 'college_portal.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            class TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            faculty_id INTEGER,
            date DATE NOT NULL,
            reason TEXT NOT NULL,
            proof TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            class_id INTEGER,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            faculty_id INTEGER,
            schedule TEXT,
            room TEXT,
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date DATE NOT NULL,
            time TEXT,
            venue TEXT,
            description TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS clubs_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default data
    # Check if admin already exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, name, email) VALUES (?, ?, ?, ?, ?)",
                 ('admin', 'admin123', 'admin', 'System Administrator', 'admin@college.edu'))
        
        # Add sample faculty
        c.execute("INSERT INTO users (username, password, role, name, email, department) VALUES (?, ?, ?, ?, ?, ?)",
                 ('faculty1', 'faculty123', 'faculty', 'Dr. Robert Brown', 'robert@college.edu', 'Computer Science'))
        c.execute("INSERT INTO users (username, password, role, name, email, department) VALUES (?, ?, ?, ?, ?, ?)",
                 ('faculty2', 'faculty123', 'faculty', 'Dr. Sarah Wilson', 'sarah@college.edu', 'Electronics'))
        
        # Add sample students
        c.execute("INSERT INTO users (username, password, role, name, email, class) VALUES (?, ?, ?, ?, ?, ?)",
                 ('student1', 'student123', 'student', 'John Doe', 'john@college.edu', 'B.Tech CSE'))
        c.execute("INSERT INTO users (username, password, role, name, email, class) VALUES (?, ?, ?, ?, ?, ?)",
                 ('student2', 'student123', 'student', 'Jane Smith', 'jane@college.edu', 'B.Tech ECE'))
        
        # Add sample classes
        c.execute("INSERT INTO classes (name, faculty_id, schedule, room) VALUES (?, ?, ?, ?)",
                 ('Mathematics', 2, 'Mon, Wed 9:00-10:00', 'Room 101'))
        c.execute("INSERT INTO classes (name, faculty_id, schedule, room) VALUES (?, ?, ?, ?)",
                 ('Physics', 3, 'Tue, Thu 11:00-12:00', 'Room 205'))
        
        # Add sample events
        c.execute("INSERT INTO events (name, date, time, venue, description) VALUES (?, ?, ?, ?, ?)",
                 ('Tech Fest 2023', '2023-11-15', '10:00 AM', 'Main Auditorium', 'Annual technical festival'))
        c.execute("INSERT INTO events (name, date, time, venue, description) VALUES (?, ?, ?, ?, ?)",
                 ('Career Guidance Workshop', '2023-11-20', '2:00 PM', 'Seminar Hall', 'Workshop on career opportunities'))
        
        # Add sample clubs and events
        clubs_events = [
            ('Tech Club', 'club'),
            ('Sports Club', 'club'),
            ('Cultural Club', 'club'),
            ('Science Club', 'club'),
            ('Annual Sports Day', 'event'),
            ('Tech Fest', 'event'),
            ('Cultural Fest', 'event'),
            ('Workshop', 'event')
        ]
        for name, type in clubs_events:
            c.execute("INSERT INTO clubs_events (name, type) VALUES (?, ?)", (name, type))
        
        # Add sample attendance
        today = date.today().isoformat()
        c.execute("INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
                 (4, 1, today, 'present'))
        c.execute("INSERT INTO attendance (student_id, class_id, date, status) VALUES (?, ?, ?, ?)",
                 (5, 1, today, 'present'))
        
        # Add sample permissions
        c.execute("INSERT INTO permissions (student_id, faculty_id, date, reason, status) VALUES (?, ?, ?, ?, ?)",
                 (4, 2, '2023-10-25', 'Medical appointment', 'pending'))
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    conn.commit()
    conn.close()

# Database helper function
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ? AND role = ?',
        (username, password, role)
    ).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['name'] = user['name']
        
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get statistics
    students_count = conn.execute('SELECT COUNT(*) FROM users WHERE role = "student"').fetchone()[0]
    faculty_count = conn.execute('SELECT COUNT(*) FROM users WHERE role = "faculty"').fetchone()[0]
    pending_permissions = conn.execute('SELECT COUNT(*) FROM permissions WHERE status = "pending"').fetchone()[0]
    events_count = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    
    # Get users
    students = conn.execute('SELECT * FROM users WHERE role = "student"').fetchall()
    faculty = conn.execute('SELECT * FROM users WHERE role = "faculty"').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         students_count=students_count,
                         faculty_count=faculty_count,
                         pending_permissions=pending_permissions,
                         events_count=events_count,
                         students=students,
                         faculty=faculty)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    faculty_id = session['user_id']
    
    # Get statistics
    classes_count = conn.execute('SELECT COUNT(*) FROM classes WHERE faculty_id = ?', (faculty_id,)).fetchone()[0]
    students_count = conn.execute('''
        SELECT COUNT(DISTINCT u.id) 
        FROM users u 
        JOIN attendance a ON u.id = a.student_id 
        JOIN classes c ON a.class_id = c.id 
        WHERE c.faculty_id = ?
    ''', (faculty_id,)).fetchone()[0]
    pending_permissions = conn.execute('SELECT COUNT(*) FROM permissions WHERE faculty_id = ? AND status = "pending"', (faculty_id,)).fetchone()[0]
    
    # Get permissions
    permissions = conn.execute('''
        SELECT p.*, u.name as student_name 
        FROM permissions p 
        JOIN users u ON p.student_id = u.id 
        WHERE p.faculty_id = ?
    ''', (faculty_id,)).fetchall()
    
    # Get classes
    classes = conn.execute('SELECT * FROM classes WHERE faculty_id = ?', (faculty_id,)).fetchall()
    
    conn.close()
    
    return render_template('faculty_dashboard.html',
                         classes_count=classes_count,
                         students_count=students_count,
                         pending_permissions=pending_permissions,
                         permissions=permissions,
                         classes=classes)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    student_id = session['user_id']
    
    # Get clubs and events for permission form
    clubs_events = conn.execute('SELECT * FROM clubs_events WHERE is_active = 1').fetchall()
    clubs = [ce for ce in clubs_events if ce['type'] == 'club']
    events = [ce for ce in clubs_events if ce['type'] == 'event']
    
    # Get statistics
    attendance_percentage = conn.execute('''
        SELECT 
            COUNT(CASE WHEN status = 'present' THEN 1 END) * 100.0 / COUNT(*) as percentage
        FROM attendance 
        WHERE student_id = ?
    ''', (student_id,)).fetchone()[0] or 0
    
    pending_permissions = conn.execute('SELECT COUNT(*) FROM permissions WHERE student_id = ? AND status = "pending"', (student_id,)).fetchone()[0]
    events_count = conn.execute('SELECT COUNT(*) FROM student_events WHERE student_id = ?', (student_id,)).fetchone()[0]
    
    # Get attendance
    attendance = conn.execute('''
        SELECT c.name, 
               COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present,
               COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent,
               COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / COUNT(*) as percentage
        FROM attendance a
        JOIN classes c ON a.class_id = c.id
        WHERE a.student_id = ?
        GROUP BY c.name
    ''', (student_id,)).fetchall()
    
    # Get permissions
    permissions = conn.execute('SELECT * FROM permissions WHERE student_id = ?', (student_id,)).fetchall()
    
    # Get events
    events_list = conn.execute('''
        SELECT e.* 
        FROM events e
        JOIN student_events se ON e.id = se.event_id
        WHERE se.student_id = ?
    ''', (student_id,)).fetchall()
    
    conn.close()
    
    return render_template('student_dashboard.html',
                         clubs=clubs,
                         events=events,
                         attendance_percentage=attendance_percentage,
                         pending_permissions=pending_permissions,
                         events_count=events_count,
                         attendance=attendance,
                         permissions=permissions,
                         events_list=events_list)

# API Routes for AJAX operations
@app.route('/api/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute('INSERT INTO users (username, password, role, name, email, class) VALUES (?, ?, ?, ?, ?, ?)',
                    (data['username'], data['password'], 'student', data['name'], 
                     data.get('email'), data.get('class')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Student added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists'})

@app.route('/api/update_permission_status', methods=['POST'])
def update_permission_status():
    if 'user_id' not in session or session['role'] != 'faculty':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    conn = get_db_connection()
    conn.execute('UPDATE permissions SET status = ? WHERE id = ?', (data['status'], data['permission_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Permission updated successfully'})

@app.route('/api/add_permission', methods=['POST'])
def add_permission():
    if 'user_id' not in session or session['role'] != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    conn = get_db_connection()
    
    # Get faculty for the student's class (simplified - in real app would need proper mapping)
    faculty = conn.execute('SELECT id FROM users WHERE role = "faculty" LIMIT 1').fetchone()
    
    if faculty:
        conn.execute('INSERT INTO permissions (student_id, faculty_id, date, reason, proof) VALUES (?, ?, ?, ?, ?)',
                    (session['user_id'], faculty['id'], data['date'], data['reason'], data.get('proof', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Permission request submitted successfully'})
    
    conn.close()
    return jsonify({'success': False, 'message': 'No faculty found'})

@app.route('/api/upload_students', methods=['POST'])
def upload_students():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        try:
            # Read Excel file
            df = pd.read_excel(file)
            required_columns = ['name', 'username', 'password', 'class']
            
            # Check required columns
            for col in required_columns:
                if col not in df.columns:
                    return jsonify({'success': False, 'message': f'Missing required column: {col}'})
            
            conn = get_db_connection()
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    conn.execute(
                        'INSERT INTO users (username, password, role, name, email, class) VALUES (?, ?, ?, ?, ?, ?)',
                        (row['username'], row['password'], 'student', row['name'], 
                         row.get('email', ''), row['class'])
                    )
                    success_count += 1
                except sqlite3.IntegrityError:
                    error_count += 1
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True, 
                'message': f'Successfully added {success_count} students. {error_count} failed due to duplicate usernames.'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'})

@app.route('/api/upload_faculty', methods=['POST'])
def upload_faculty():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        try:
            df = pd.read_excel(file)
            required_columns = ['name', 'username', 'password', 'department']
            
            for col in required_columns:
                if col not in df.columns:
                    return jsonify({'success': False, 'message': f'Missing required column: {col}'})
            
            conn = get_db_connection()
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    conn.execute(
                        'INSERT INTO users (username, password, role, name, email, department) VALUES (?, ?, ?, ?, ?, ?)',
                        (row['username'], row['password'], 'faculty', row['name'], 
                         row.get('email', ''), row['department'])
                    )
                    success_count += 1
                except sqlite3.IntegrityError:
                    error_count += 1
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True, 
                'message': f'Successfully added {success_count} faculty. {error_count} failed due to duplicate usernames.'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'})

@app.route('/api/add_faculty', methods=['POST'])
def add_faculty():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute(
            'INSERT INTO users (username, password, role, name, email, department) VALUES (?, ?, ?, ?, ?, ?)',
            (data['username'], data['password'], 'faculty', data['name'], 
             data.get('email'), data.get('department'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Faculty added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists'})

@app.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error deleting user: {str(e)}'})

@app.route('/api/get_clubs_events')
def get_clubs_events():
    conn = get_db_connection()
    clubs_events = conn.execute('SELECT * FROM clubs_events WHERE is_active = 1').fetchall()
    conn.close()
    
    clubs = [{'id': ce['id'], 'name': ce['name'], 'type': ce['type']} 
             for ce in clubs_events if ce['type'] == 'club']
    events = [{'id': ce['id'], 'name': ce['name'], 'type': ce['type']} 
              for ce in clubs_events if ce['type'] == 'event']
    
    return jsonify({'clubs': clubs, 'events': events})

@app.route('/api/add_club_event', methods=['POST'])
def add_club_event():
    if 'user_id' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute(
            'INSERT INTO clubs_events (name, type) VALUES (?, ?)',
            (data['name'], data['type'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'{data["type"].title()} added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    user_id = session['user_id']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user or user['password'] != data['current_password']:
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    if data['new_password'] != data['confirm_password']:
        conn.close()
        return jsonify({'success': False, 'message': 'New passwords do not match'})
    
    try:
        conn.execute('UPDATE users SET password = ? WHERE id = ?', (data['new_password'], user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Error changing password: {str(e)}'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)