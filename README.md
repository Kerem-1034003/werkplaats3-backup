# Werkplaats-3-inhaalopdracht-actiontypes

Project ActionTypes. An application where students can answer statements and where an action type result is calculated so that the teacher can form teams using the student overview.

# Developers

Kerem Yildiz (1034004)

# Installeren requirements

pip install virtualenv

virtualenv venv

.\venv\scripts\activate

pip install -r requirements.txt

# Starten van applicatie

.\venv\scripts\activate

set FLASK_APP=main.py

set FLASK_DEBUG=true

set SECRET_KEY=e92a82afe456e18d535c6602d9d57644

or

export FLASK_APP=main.py

export FLASK_DEBUG=true

export BLOGFUL_SECRET_KEY=e92a82afe456e18d535c6602d9d57644

flask run

http://127.0.0.1:5000

# Studentscreen Test

- Click on "Studenten" in the navbar.
- Enter your student number, for example (1772998), and click on "volgende vraag."
- Click on one of the 2 statements that appear.
- Click on "Next question" and select one of the 2 statements. Repeat this process until no more statements appear.
- Then, make a GET request in Postman as follows: http://localhost:5000/api/student/1772998/actiontype
- The action type will be calculated and saved.

# Teacherscreen Test

- Click on "Docenten" in the navbar.
- Log in with the following credentials (username: Kerem, password: Kerem10).
- An overview of the students with their student number, name, class, action type, date filled, and team will be displayed.
- To add a new student, enter the details and click on "toevoegen."
- Refresh the page and use the filter to search for the student by student number, name, or class.
- When you click on "verwijder antwoorde" behind a student, all answered statements will be deleted, allowing the student to answer statements again.
- Clicking on the "wijzig" button will take you to the detail screen.

# Detailscreen Test

- Enter the student number.
- An overview of the student with their details will appear.
- You can also see the answered statements if they have been filled out.
- Modify the student's details if necessary.
- Save the new/current details by clicking on "toevoegen."
- Refresh the screen, and you will see the updated student details.

# Admin role Test

- Click on "Teacher" in the navbar.
- Log in with the following credentials (username: Mark, password: Mark10).
- Adding a teacher is not possible yet .

# Recources

- https://flask.palletsprojects.com/en/3.0.x/
- https://flask.palletsprojects.com/en/3.0.x/quickstart/#routing
- https://flask.palletsprojects.com/en/3.0.x/quickstart/#apis-with-json
- https://www.w3schools.com/js/
- https://getbootstrap.com/
- https://www.youtube.com/watch?v=qbLc5a9jdXo
- https://www.youtube.com/watch?v=-XchxUQTcfQ
- https://flask.palletsprojects.com/en/3.0.x/patterns/javascript/

# Version

Current version v1.0 Release date 17-04-2023

# Bugs

1.  Adding a teacher is not working
