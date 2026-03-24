from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
db_file = 'QLGiangvien.db'


def get_db_connection():
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


@app.route('/')
def index():
    # Public Search Functionality (Pic 3)
    search_query = request.args.get('search', '')
    connection = get_db_connection()

    if search_query:
        # Search requirement: name or position [cite: 30, 67]
        query = "SELECT * FROM lecturer WHERE name LIKE ? OR position LIKE ?"
        lecturers = connection.execute(query, (f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        lecturers = connection.execute('SELECT * FROM lecturer').fetchall()

    connection.close()
    return render_template('index.html', lecturers=lecturers)


@app.route('/lecturer/<int:id>')
def profile(id):
    connection = get_db_connection()
    # Fetch data for Pic 2 layout
    lecturer = connection.execute('SELECT * FROM lecturer WHERE lecturer_id = ?', (id,)).fetchone()
    education = connection.execute('SELECT * FROM education WHERE lecturer_id = ?', (id,)).fetchall()
    experience = connection.execute('SELECT * FROM experience WHERE lecturer_id = ?', (id,)).fetchall()
    connection.close()
    return render_template('profile.html', lecturer=lecturer, education=education, experience=experience)


if __name__ == '__main__':
    # Running on default port 5000
    app.run(port=5000, debug=True)
