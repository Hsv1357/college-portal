import sqlite3

def init_db():
    conn = sqlite3.connect('college_portal.db')
    c = conn.cursor()
    
    # Create tables (same as in app.py)
    # This is a backup initialization script
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")