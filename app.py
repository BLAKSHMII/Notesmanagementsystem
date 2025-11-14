from flask import Flask, render_template, request, redirect, session,flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret123"
# Session lifetime
app.permanent_session_lifetime = timedelta(days=90)

# MySQL Connection
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="lakshmi@12",
    database="codegnan"
)
cursor = con.cursor(dictionary=True)



# ---------------- HOME (Notes List) ----------------
@app.route('/')
def home():
    if "username" not in session:
        return redirect('/login')

    username = session['username']
    cursor.execute("SELECT * FROM notes WHERE username=%s", (username,))
    notes = cursor.fetchall()

    return render_template('home.html', notes=notes)



# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user:
            return "Username already exists"

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                       (username, password))
        con.commit()
        return redirect('/login')

    return render_template('register.html')



# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        session.permanent = True

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect('/')
        else:
            return "Invalid username or password"

    return render_template('login.html')



# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')



# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':

        username = request.form['username']
        newpass = generate_password_hash(request.form['password'])

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if not user:
            return "Username not found!"

        cursor.execute("UPDATE users SET password=%s WHERE username=%s",
                       (newpass, username))
        con.commit()
        return redirect('/login') #"Password updated! <a href='/login'>Login</a>"

    return render_template('forgot.html')



# ---------------- ADD NOTE ----------------
@app.route('/add', methods=['GET','POST'])
def add():
    if "username" not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        username = session['username']

        cursor.execute("INSERT INTO notes (title, content, username) VALUES (%s,%s,%s)",
                       (title, content, username))
        con.commit()

        return redirect('/')

    return render_template('add.html')



# ---------------- EDIT NOTE ----------------
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if "username" not in session:
        return redirect('/login')

    cursor.execute("SELECT * FROM notes WHERE id=%s AND username=%s",
                   (id, session['username']))
    note = cursor.fetchone()

    if not note:
        return "Note not found"

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        cursor.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s",
                       (title, content, id))
        con.commit()

        return redirect('/')

    return render_template('edit.html', note=note)



# ---------------- DELETE NOTE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if "username" not in session:
        return redirect('/login')

    cursor.execute("DELETE FROM notes WHERE id=%s AND username=%s",
                   (id, session['username']))
    con.commit()

    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)
