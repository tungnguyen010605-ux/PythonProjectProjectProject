from flask import Flask, session, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Felix Pham'  # [cite: 30]

# Path to your database
db_file = 'db/QLGiangvien.db'  # [cite: 30]


def get_db_connection():
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


# --- PUBLIC & SHARED ROUTES ---

@app.route('/')
def index():
    # Search and Sort Parameters [cite: 30, 67]
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'name')

    # Allowed columns for sorting from your database [cite: 30, 149]
    allowed_sorts = ['name', 'title', 'position', 'department', 'research_field']
    if sort_by not in allowed_sorts:
        sort_by = 'name'

    connection = get_db_connection()

    # Build query based on requirements [cite: 30, 67]
    if search_query:
        query = f"SELECT * FROM lecturer WHERE name LIKE ? OR position LIKE ? ORDER BY {sort_by} ASC"
        wildcard = f"%{search_query}%"
        lecturers = connection.execute(query, (wildcard, wildcard)).fetchall()
    else:
        query = f"SELECT * FROM lecturer ORDER BY {sort_by} ASC"
        lecturers = connection.execute(query).fetchall()

    connection.close()

    # If admin is logged in, you can choose to redirect them to a dashboard
    # or just show admin buttons on this main page.
    return render_template('index.html', lecturers=lecturers, search_query=search_query, current_sort=sort_by)


@app.route('/lecturer/<int:id>')
def profile(id):
    connection = get_db_connection()
    # Fetch data for Pic 2 layout [cite: 30, 149]
    lecturer = connection.execute('SELECT * FROM lecturer WHERE lecturer_id = ?', (id,)).fetchone()
    education = connection.execute('SELECT * FROM education WHERE lecturer_id = ?', (id,)).fetchall()
    experience = connection.execute('SELECT * FROM experience WHERE lecturer_id = ?', (id,)).fetchall()
    connection.close()
    return render_template('profile.html', lecturer=lecturer, education=education, experience=experience)


# --- AUTHENTICATION ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '123':
            session['logged_in'] = True
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('index'))
    return render_template('admin/login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


# --- ADMIN PRIVILEGED ROUTES ---

@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if request.method == 'POST':
        data = (request.form['name'], request.form['title'], request.form['position'],
                request.form['email'], request.form['phone'])  # [cite: 30, 67]
        conn = get_db_connection()
        conn.execute('INSERT INTO lecturer (name, title, position, email, phone) VALUES (?,?,?,?,?)', data)
        conn.commit()
        conn.close()
        flash('Lecturer Added Successfully!')
        return redirect(url_for('index'))
    return render_template('admin/add.html')


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        data = (request.form['name'], request.form['title'], request.form['position'], id)
        conn.execute('UPDATE lecturer SET name=?, title=?, position=? WHERE lecturer_id=?', data)
        conn.commit()
        conn.close()
        flash('Lecturer Updated!')
        return redirect(url_for('index'))

    lecturer = conn.execute('SELECT * FROM lecturer WHERE lecturer_id = ?', (id,)).fetchone()
    conn.close()
    return render_template('admin/edit.html', lecturer=lecturer)


@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM lecturer WHERE lecturer_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Lecturer Deleted!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Running on default port 5000
    app.run(port=5000, debug=True)