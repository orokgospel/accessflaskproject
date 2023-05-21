import random
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.debug = True
app.secret_key = 'your_secret_key'  # Set a secret key for session encryption


def create_users_table():
    # Create the 'users' table if it doesn't exist
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, emailaddress TEXT, firstname TEXT, lastname TEXT, residentkey TEXT)")
    conn.commit()
    c.close()
    conn.close()


@app.route('/')
def landing():
    return render_template('index.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        emailaddress = request.form['emailaddress']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        residentkey = request.form['residentkey']

        # Validate form data
        if password != confirm_password:
            error_message = "Passwords do not match."
            return render_template('create_account.html', error=error_message)
        elif residentkey!="NELNA23":
            error_message="Please enter correct resident key."
            return render_template('create_account.html', error=error_message)

        try:
            # Create 'users' table if it doesn't exist
            create_users_table()

            # Create a new SQLite connection and cursor for each request
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # Check if username already exists in the database
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                error_message = "Username already exists."
                return render_template('create_account.html', error=error_message)

            # Store user account in the database
            c.execute(
                "INSERT INTO users (username, password, emailaddress, firstname, lastname, residentkey) VALUES (?, ?, ?, ?, ?, ?)",
                (username, password, emailaddress, firstname, lastname, residentkey))
            conn.commit()

            # Redirect to login page
            return redirect('/login')
        
       
        finally:
            # Close the cursor and connection after each request
            c.close()
            conn.close()

    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # Create 'users' table if it doesn't exist
            create_users_table()

            # Create a new SQLite connection and cursor for each request
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # Validate form data
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            if not c.fetchone():
                error_message = "Invalid username or password."
                return render_template('login.html', error=error_message)

            # Perform user authentication and set session variable
            session['username'] = username

            # Redirect to homepage or any other authenticated route
            return redirect('/generate_code')
        
        except sqlite3.Error as e:
            # Handle any database-related errors
            error_message = "An error occurred while logging in."
            return render_template('login.html', error=error_message)
            
        finally:
            # Close the cursor and connection after each request
            c.close()
            conn.close()
    else:
        # Create a new SQLite connection and cursor for GET request
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.close()
        conn.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear session variable to indicate user logout
    session.clear()

    # Redirect to login page or homepage
    return redirect('/login')

@app.route('/generate_code', methods=['GET', 'POST'])
def generate_code():
    if request.method == 'POST':
        # Handle the form submission and generate the access code
        visitor_name = request.form['visitorname']
        visit_address = request.form['visitaddress']
        resident_name = request.form['residentname']
        arrival_day = request.form['arrivalday']
        arrival_time = request.form['arrivaltime']

        # Generate a code by subtracting 23 repeatedly from 7000
        serial_start = 7000
        serial_end = 4000

        code = serial_start
        while code >= serial_end:
            code -= 23

        # Reshuffle the digits of the code
            code_digits = list(str(code))
            random.shuffle(code_digits)
            reshuffled_code = int(''.join(code_digits))

        return render_template('generate_code.html', code=reshuffled_code)
    return render_template('generate_code.html')

if __name__ == '__main__':
    app.run()