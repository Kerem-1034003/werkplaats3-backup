import sqlite3
import json
from os import environ
import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session, g, jsonify
from forms import LoginForm
from markupsafe import Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#Routes 

@app.route("/")
def home():
    return render_template('home.html', title='Home')

@app.before_request
def before_request():
    g.gebruikersnaam = None

    if 'gebruikersnaam' in session:
        g.gebruikersnaam = session['gebruikersnaam']

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    con = sqlite3.connect('database.db')
    con.row_factory=sqlite3.Row
    cur = con.cursor()
    if request.method == 'POST':
            session.pop('username', None)
            username = request.form['gebruikersnaam']
            password = request.form['wachtwoord']
            cur = con.cursor()
            cur.execute("SELECT username, password, role FROM teachers WHERE username=? and password=?",(username, password))
            data = cur.fetchone()

            if data:
                session["gebruikersnaam"] = data[0]
                session["wachtwoord"] = data[1]
                session["role"] = data[2]  # Opnemen van de rol in de sessie
                if data[2] == 'admin':
                    return render_template('admindocent.html')  # Doorsturen naar admin dashboard
                else:
                    return redirect(url_for('homedocent'))  # Doorsturen naar docent dashboard
            else:
                flash("gebruikersnaam of wachtwoord is onjuist")

    return render_template('logindocent.html', title='Log in', form=form)

@app.route("/add_teacher", methods=['POST', 'GET'])
def add_teacher():
    if 'username' not in session or session['role'] != 'admin':
        # Als de gebruiker niet is ingelogd of geen admin is, doorsturen naar de inlogpagina
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Ontvang de gegevens van het formulier om een nieuwe docent toe te voegen
    name= request.form['name']
    username = request.form['username']
    password = request.form['password'] 
    role = request.form['role']
    # Voeg de nieuwe docent toe aan de database
    cursor.execute("INSERT INTO teachers (name, username, password, role) VALUES (?, ?, ?, ?)", (name, username, password, role))
    conn.commit()
    conn.close()
    flash('Docent succesvol toegevoegd!')
    return render_template('admindocent.html')

@app.route('/logout')
def logout():
    session.pop('gebruikersnaam', None)
    return redirect(url_for('login'))

@app.route('/getsession')
def getsession():
    if 'gebruikersnaam' in session:
        gebruikersnaam = session['gebruikersnaam']
        return f"Welcome {gebruikersnaam}"
    else:
        return "Welcome Anonymous"

@app.route("/homedocent", methods=['GET', 'POST'])
def homedocent():
    if g.gebruikersnaam:
        return render_template('homedocent.html', gebruiker=session['gebruikersnaam'])
    return redirect(url_for('login'))

@app.route("/homestudent", methods=['GET','POST'])
def homestudent():
    return render_template('homestudent.html')

@app.route("/detail", methods=['GET', 'POST'])
def detail():
    if g.gebruikersnaam:
        return render_template('detailstudent.html', gebruiker=session['gebruikersnaam'])
    return redirect(url_for('login'))

# Studenten Invoegen
def insert_students():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    with open('students.json', 'r') as file:
        students_data = json.load(file)

    for student in students_data:
        # Controleer of de student al bestaat in de database
        cursor.execute('SELECT * FROM students WHERE student_number = ?', (student['student_number'],))
        existing_student = cursor.fetchone()

        if existing_student is None:
            # Voeg de student toe als deze nog niet bestaat
            cursor.execute('''
                INSERT INTO students (student_number, name, class)
                VALUES (?, ?, ?)
            ''', (
                student['student_number'],
                student['student_name'],
                student['student_class']
            ))
        else:
            print(f"Student met student_number {student['student_number']} bestaat al in de database.")

    conn.commit()
    conn.close()

# Statements Invoegen
def insert_statements():
    print("Invoegen van statements...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    print("Connectie gelukt")

    with open('actiontype_statements.json', 'r') as file:
        statements_data = json.load(file)
    print("Bestand ingelezen")

    try:
        for statement in statements_data:
            for choice in statement['statement_choices']:
                statement_number = statement['statement_number']
                print(f"Inserting statement_number: {statement_number}")

                cursor.execute('''
                    INSERT INTO statements (statement_number, choice_number, choice_text, choice_result)
                    VALUES (?, ?, ?, ?)
                ''', (
                    statement['statement_number'],
                    choice['choice_number'],
                    choice['choice_text'],
                    choice['choice_result']
                ))

        conn.commit()
        print("Invoegen van statements voltooid.")

    except Exception as e:
        print(f"Fout bij het invoegen van statements: {e}")

    finally:
        conn.close()
        print("Connectie gesloten.")


# Gegevens Ophalen
def retrieve_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()

    for student in students:
        print(student)

    conn.close()

# GET & POST routes statements

@app.route("/api/student/<int:student_number>/statement", methods=["GET"])
def get_next_statement(student_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Query om de volgende onbeantwoorde stelling op te halen voor de student
    query = """
            SELECT statement_number, choice_number, choice_text
            FROM statements
            WHERE statement_number NOT IN (
                SELECT statement_number
                FROM student_answers
                WHERE student_number = ?
            )
            """
    cursor.execute(query, (student_number,))
    results = cursor.fetchall()

    # Als er resultaten zijn, maak een JSON-reactie en retourneer deze
    if results:
        statements = []
        for result in results:
            statement_number, choice_number, choice_text = result
            statements.append({
                "statement_number": statement_number,
                "choice_number": choice_number,
                "choice_text": choice_text
            })
        return jsonify(statements)
    else:
        # Als er geen onbeantwoorde stellingen meer zijn, retourneer een foutmelding
        return jsonify({"error": "Geen onbeantwoorde stellingen meer voor deze student"})

@app.route('/api/student/<int:student_number>/statement/<int:statement_number>', methods=['POST', 'GET'])
def save_statement_choice(student_number, statement_number):
    if 'choice_number' not in request.json:
        return jsonify({"error": "Keuzenummer ontbreekt in het verzoek."}), 400
    
    choice_number = request.json.get('choice_number')

    choice_result = get_choice_result(statement_number, choice_number)

    current_date = datetime.datetime.now().date().isoformat()  

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO student_answers (student_number, statement_number, choice_number, choice_result, answer_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_number, statement_number, choice_number, choice_result, current_date))
        conn.commit()
        conn.close()
        return jsonify({"result": "ok"})
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": "Er is een fout opgetreden bij het opslaan van het antwoord."}), 500

def get_choice_result(statement_number, choice_number):
    if statement_number in [1, 5, 9, 13, 17]:
        return 'E' if choice_number == 1 else 'I'
    elif statement_number in [2, 6, 10, 14, 18]:
        return 'S' if choice_number == 1 else 'N'
    elif statement_number in [3, 7, 11, 15, 19]:
        return 'T' if choice_number == 1 else 'F'
    elif statement_number in [4, 8, 12, 16, 20]:
        return 'J' if choice_number == 1 else 'P'

    
@app.route("/api/student/<int:student_number>/actiontype", methods=['GET','POST'])
def calculate_and_save_action_type(student_number):
    action_type = calculate_action_type(student_number)
    if action_type:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students
            SET action_type = ?
            WHERE student_number = ?
        ''', (action_type, student_number))
        conn.commit()
        conn.close()
        return jsonify({"success": "Action Type succesvol berekend en opgeslagen", "action_type": action_type}), 200
    else:
        return jsonify({"error": "Kon het Action Type niet berekenen"}), 500
    
def calculate_action_type(student_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Haal alle keuzes op die de student heeft gemaakt voor de beantwoorde stellingen
    cursor.execute('''
        SELECT choice_result 
        FROM student_answers
        WHERE student_number = ?
    ''', (student_number,))
    choices = cursor.fetchall()

    print("Alle keuzes van de student:", choices)

    conn.close()

    # Tel het aantal keer dat elke keuze is gemaakt
    choice_counts = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    for choice in choices:
        choice_counts[choice[0]] += 1

    print("Telling van keuzes:", choice_counts)

    # Bepaal welke keuze het meest voorkomt
    action_type = ''
    for category in ['E', 'I', 'S', 'N', 'T', 'F', 'J', 'P']:
        if choice_counts[category] > 2:  # Hier veronderstellen we dat 20 vragen zijn beantwoord
            action_type += category

    return action_type


@app.route('/api/student/<int:student_number>/info', methods=['GET'])
def get_student_info(student_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, class
        FROM students
        WHERE student_number = ?
    ''', (student_number,))
    student_info = cursor.fetchone()  # Ophalen van de studentinformatie
    conn.close()
    if student_info:
        # Retourneer de studentinformatie als JSON
        return jsonify({"name": student_info[0], "class": student_info[1]})
    else:
        return jsonify({"error": "Student not found"}), 404
    
# Beheer pagina toevoegen studenten
@app.route('/add_student', methods=['POST'])
def add_student():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Studentgegevens ophalen uit het formulier
    student_number = request.form['student_number']
    name = request.form['name']
    class_name = request.form['class']
    # Nieuwe student toevoegen aan de database
    cursor.execute('INSERT INTO students (student_number, name, class) VALUES (?, ?, ?)', (student_number, name, class_name))
    conn.commit()  # Vergeet niet om wijzigingen door te voeren
    return redirect(url_for('homedocent'))

# Beheer pagina ophalen studenten
@app.route("/api/students", methods=["GET"])
def get_all_students():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Haal alle studenten op uit de database
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()

    # Maak een lijst van dictionaries met studentgegevens
    student_list = []
    for student in students:
        student_dict = {
            "student_number": student[0],
            "name": student[1],
            "class": student[2],
            "action_type": student[3],
            "team": student[4]
        }
        student_list.append(student_dict)

    conn.close()
    # Retourneer de lijst met studenten als JSON
    return jsonify(student_list)

# Beheer pagina verwijderen van stellingen per student
@app.route('/api/students/<int:student_number>/answers', methods=['DELETE'])
def delete_student_answers(student_number):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Verwijder antwoorden van de student uit de database
        cursor.execute('DELETE FROM student_answers WHERE student_number = ?', (student_number,))
        conn.commit()

        cursor.execute('UPDATE students SET action_type = NULL WHERE student_number = ?', (student_number,))
        conn.commit()

        conn.close()

        return jsonify({'message': f'Antwoorden van student {student_number} zijn succesvol verwijderd.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Datum weergeven - Beheerpagina     
@app.route('/api/student/last_answer_date/<int:student_number>', methods=['GET'])
def get_last_answer_date(student_number):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Voer een query uit om de datum van de laatste beantwoorde stelling op te halen
        cursor.execute('''
            SELECT MAX(answer_date) FROM student_answers WHERE student_number = ?
        ''', (student_number,))
        last_answer_date = cursor.fetchone()[0]

        conn.close()

        return jsonify({"last_answer_date": last_answer_date})

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

# Voeg deze route toe aan je Flask-app
@app.route("/api/student/<int:student_number>", methods=['GET'])
def get_student_details(student_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Haal de gegevens van de student op uit de database op basis van het studentnummer
    cursor.execute('''
        SELECT student_number, name, class, team
        FROM students
        WHERE student_number = ?
    ''', (student_number,))
    student_info = cursor.fetchone()

    conn.close()

    # Controleer of de student is gevonden in de database
    if student_info:
        # Retourneer de gegevens van de student als een JSON-respons
        return jsonify({
            "student_number": student_info[0],
            "name": student_info[1],
            "class": student_info[2],
            "team": student_info[3]
        }), 200
    else:
        # Als de student niet is gevonden, retourneer een foutmelding
        return jsonify({"error": "Student not found"}), 404

# detailscherm student wijzigen
@app.route("/api/update_student", methods=['POST'])
def update_student():
    # Ontvang de nieuwe gegevens van de student uit het JSON-verzoek
    data = request.json
    student_number = data.get('student_number')
    name = data.get('name')
    class_ = data.get('class')
    team = data.get('team')

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Update de gegevens van de student in de database
        cursor.execute('''
            UPDATE students
            SET name = ?, class = ?, team = ?
            WHERE student_number = ?
        ''', (name, class_, team, student_number))
        conn.commit()
        conn.close()

        # Retourneer een JSON-respons om aan te geven dat de wijzigingen zijn doorgevoerd
        return jsonify({"message": "Studentgegevens succesvol bijgewerkt"}), 200
    except sqlite3.Error as e:
        # Retourneer een foutmelding als er een fout optreedt bij het bijwerken van de gegevens
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500
    
# detailscherm beantowoorde stellingen ophalen    
@app.route("/api/student/<int:student_number>/answered_statements", methods=["GET"])
def get_answered_statements(student_number):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Query om de beantwoorde stellingen van de student op te halen
    cursor.execute('''
        SELECT statement_number, choice_number, choice_result
        FROM student_answers
        WHERE student_number = ?
    ''', (student_number,))
    answered_statements = cursor.fetchall()

    # Lijst om de keuzeteksten op te slaan
    choices = []

    # Voor elke beantwoorde stelling, haal de keuzetekst op uit de statements tabel
    for statement in answered_statements:
        statement_number, choice_number, _ = statement
        cursor.execute('''
            SELECT choice_text
            FROM statements
            WHERE statement_number = ? AND choice_number = ?
        ''', (statement_number, choice_number))
        choice_text = cursor.fetchone()
        if choice_text:
            choices.append(choice_text[0])

    conn.close()

    # Retourneer de lijst met keuzeteksten als JSON
    return jsonify(choices)
    
    
# Uitvoeren van de functies
if __name__ == "__main__":
    insert_statements()
    insert_students()
    retrieve_data()
    app.run(debug=True)
