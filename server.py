from flask import Flask, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'database1'
app.secret_key = 'your_secret_key'  # You should set a secret key for session management

mysql = MySQL(app)

# Create the users table if not exists (Inside app context)
with app.app_context():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
    ''')
    mysql.connection.commit()

# Route for login details
@app.route('/login_details', methods=['POST'])
def login_details():
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Query the users table
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        # If password is correct, redirect to success page
        session['user_id'] = user['id']  # Store user id in session
        return redirect(url_for('mininew'))
    else:
        # If login fails, redirect to failure page
        return redirect(url_for('login_failure'))

# Route for registration
@app.route('/registration', methods=['POST']) 
def registration():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#jacob
    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if user:
        # If the user exists, redirect to failure page
        return redirect(url_for('registration_failure'))
    else:
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the new user into the users table
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                       (username, email, hashed_password))
        mysql.connection.commit()
        return redirect(url_for('slogin'))

# Route for index page
@app.route('/')
def index():
    return render_template('index.html')

# Other routes for various pages
@app.route('/blogin')
def blogin():
    return render_template('blogin.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/crafts')
def crafts():
    return render_template('crafts.html')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/mininew')
def mininew():
    return render_template('mininew.html')

@app.route('/painting')
def painting():
    return render_template('painting.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/ptj')
def ptj():
    return render_template('ptj.html')

@app.route('/sellerlogin')
def sellerlogin():
    return render_template('sellerlogin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/slogin')
def slogin():
    return render_template('slogin.html')

# Success or failure pages
@app.route('/login_success')
def login_success():
    return 'Login successful!'

@app.route('/login_failure')
def login_failure():
    return 'Login failed! Please check your username and password.'

@app.route('/registration_success')
def registration_success():
    return 'Registration successful!'

@app.route('/registration_failure')
def registration_failure():
    return 'Registration failed! Username already exists.'

if __name__ == '__main__':
    app.run(debug=True)
