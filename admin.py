from flask import Flask,session, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Felix Pham'

# Path to the uploaded database
db_file = 'QLGiangvien.db'

def get_db_connection():
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


# Simple Admin Login Logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('Admin/login.html')


@app.route('/admin')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    connection = get_db_connection()
    lecturers = connection.execute('SELECT * FROM lecturer').fetchall()
    connection.close()
    return render_template('Admin/index.html', lecturers=lecturers)


@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if request.method == 'POST':
        data = (request.form['name'], request.form['title'], request.form['position'],
                request.form['email'], request.form['phone'])
        conn = get_db_connection()
        conn.execute('INSERT INTO lecturer (name, title, position, email, phone) VALUES (?,?,?,?,?)', data)
        conn.commit()
        conn.close()
        flash('Lecturer Added!')
        return redirect(url_for('dashboard'))
    return render_template('Admin/add.html')


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        data = (request.form['name'], request.form['title'], request.form['position'], id)
        conn.execute('UPDATE lecturer SET name=?, title=?, position=? WHERE lecturer_id=?', data)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    lecturer = conn.execute('SELECT * FROM lecturer WHERE lecturer_id = ?', (id,)).fetchone()
    conn.close()
    return render_template('Admin/edit.html', lecturer=lecturer)


@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM lecturer WHERE lecturer_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with User App
    app.run(port=5001, debug=True)