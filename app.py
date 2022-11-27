from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from dotenv import load_dotenv
import os

load_dotenv('.env')
#Creating instance of flask
app = Flask(__name__)
#Configure MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')
#Initialize MySQL
mysql = MySQL(app)

get_articles = Articles()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = get_articles) #Extracting data articles

# @app.route('/single_article/<string:id>/')
# def articles(id):
#     return render_template('single_article.html', id=id)

class RegisterForm(Form):
    #Creating the fields of the form
    name = StringField('Name', [validators.Length(min=2, max=50), validators.DataRequired()])
    username = StringField('Username', [validators.Length(min=2, max=25), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=50), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_pass', message='Passwords do not match')
    ])
    confirm_pass = PasswordField('Confirm Password')

@app.route("/register", methods=['GET', 'POST'])
def register():
    # Create a form variable and set it to the form class
    form = RegisterForm(request.form)
    # Check request to see whether it's POST or GET request
    if request.method == 'POST' and form.validate():
        #Extracting data from form
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Create cursor for MySQL
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        #Commit to DB
        mysql.connection.commit()
        #Close connection
        cur.close()

        flash('User successfully created', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        login_email = request.form['email']
        login_password = request.form['password']
        #Create cursor for MySQL
        cur = mysql.connection.cursor()
        #Get user by username
        result = cur.execute("SELECT * FROM user WHERE email = %s", [login_email])

        if result > 0:
            # Get stored hashed password
            data = cur.fetchone()
            password = data['password']

            #Compare passwords
            if sha256_crypt.verify(login_password, password):
                #If all login details pass
                session['logged_in'] = True
                session['email'] = login_email

                flash("Successfully logged in", "success")
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Function to bar intruders from accessing pages 
# from address bar if not logged in
# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized! Please login first', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.secret_key=os.getenv('APP.SECRET_KEY')
    app.run(debug=True)