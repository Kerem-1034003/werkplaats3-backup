import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number INTEGER,
            statement_number INTEGER,
            choice_number INTEGER,
            answer_data DATETIME
            FOREIGN KEY (student_number) REFERENCES students(student_number),
            FOREIGN KEY (statement_number) REFERENCES statements(statement_number)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            statement_number INTEGER,
            choice_number INTEGER,
            choice_text TEXT,
            choice_result TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_number INTEGER PRIMARY KEY,
            name TEXT,
            class TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT,
            password TEXT
        )
    ''')   
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
