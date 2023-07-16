import random
from flask import Flask, render_template, request, redirect, session
import sqlite3
import datetime

import qrcode
from PIL import Image
from io import BytesIO
import base64



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
        residentkey = request.form['residentkey']
        emailaddress = request.form['emailaddress']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        

        # Validate form data
        if password != confirm_password:
            error_message = "Passwords do not match."
            return render_template('create_account.html', error=error_message)
        elif residentkey != "NELNA23":
                error_message = "Please enter correct resident key."
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
        
            # Redirect to login page with success message
            return render_template('create_account.html', message="Account successfully created!")


        finally:
            # Close the cursor and connection after each request
            c.close()
            conn.close()
            
    return render_template('create_account.html',message="")  # No error initially



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



@app.route('/generate_code', methods=['GET', 'POST'])

def generate_code():
    if request.method == 'POST':
        # Handle the form submission and generate the access code
        visitorname = request.form['visitorname']
        visitaddress = request.form['visitaddress']
        hostname = request.form['hostname']
        arrivalday = request.form['arrivalday']
        arrivaltime = request.form['arrivaltime']
        deactivationdate = request.form['deactivationdate']

        current_date = datetime.date.today()  # Get the current date
        code = random.randint(4000, 7000)  # Generate a random 4-digit code

        # Create 'visitors' table if it doesn't exist
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS visitors (visitorname TEXT, visitaddress TEXT, hostname TEXT, arrivalday TEXT, arrivaltime TEXT, deactivationdate TEXT, code TEXT)")
        conn.commit()

        # Check if the generated code already exists in the database
        c.execute("SELECT * FROM visitors WHERE code = ?", (str(code),))
        existing_code = c.fetchone()

        # Change the code if it already exists
        while existing_code:
            code = random.randint(4000, 7000)
            c.execute("SELECT * FROM visitors WHERE code = ?", (str(code),))
            existing_code = c.fetchone()

        # Store visitor details in the 'visitors' table
        c.execute(
            "INSERT INTO visitors (visitorname, visitaddress, hostname, arrivalday, arrivaltime, deactivationdate, code) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (visitorname, visitaddress, hostname, arrivalday, arrivaltime, deactivationdate, str(code)))
        conn.commit()

        # Close the cursor and connection after each request
        c.close()
        conn.close()

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(code))
        qr.make(fit=True)
        qr_image = qr.make_image(fill='black', back_color='white')

        # Create a buffer to save the image
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_image_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render_template('generate_code.html', access="Access Code Successfully Generated!", code=code, qr_image=qr_image_str)
    return render_template('generate_code.html')



if __name__ == '__main__':
    app.run()
