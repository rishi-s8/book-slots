from itertools import chain
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField, SelectField
from passlib.context import CryptContext
from functools import wraps
from wtforms import form

from wtforms.fields.core import DateTimeField, TimeField
cryptcontext = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'c4dfedBooking'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please log in.', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('home.html', users = users)

@app.route('/user/<string:username>')
@is_logged_in
def user(username):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users where username = %s", [username])
    user = cur.fetchone()
    cur.close()
    return render_template('user.html', user = user)


class RegisterForm(Form):
    typeList = [('Institute', 'Institute'), ('Academic', 'Academic'), ('Other','Other')]
    name = StringField('Name', [validators.Length(min=1, max=50), validators.DataRequired()])
    username = StringField('E-mail ID', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired(), validators.EqualTo('confirm', message='Passwords Do not match')])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    accountType = SelectField('Account Type', choices=typeList)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = cryptcontext.hash(str(form.password.data))
        accountType = form.accountType.data

        print(name, username, password, accountType)

        #Create Cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        
        if(result == 0):
            cur.execute("INSERT INTO users(name, username, password, accountType) Values(%s, %s, %s, %s)", (name, username, password, accountType))
            mysql.connection.commit()
            flash("Registered Successfully", "success")

        else:
            error = 'An account already exists with this email address.'
            return render_template('register.html', error= error, form=form)

        #Close Connection
        cur.close()

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users where username = %s", [username])
        if result>0:
            data = cur.fetchone()
            password = data['password']

            if cryptcontext.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash("You are now logged in", 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error= error)
        else:
            error = 'Invalid Login'
            return render_template('login.html', error= error)
        cur.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Equipments")
    users = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', Equipments = users)
    cur.close()

class BookingForm(Form):
    SuperviserName = StringField('Superviser Name', [validators.Length(min=1, max=255), validators.DataRequired()])
    SuperviserEmail = StringField('Superviser Email', [validators.Length(min=1), validators.DataRequired()])
    From = DateTimeField("From: ", [validators.DataRequired()])
    To = DateTimeField("To: ", [validators.DataRequired()])

@app.route('/book_slot/<int:EquipID>', methods=['GET', 'POST'])
@is_logged_in
def book_slot(EquipID):
    form = BookingForm(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT id FROM Equipments where id = %s", [EquipID])
    EquipId = cur.fetchone()['id']
    username = session['username']
    result = cur.execute("SELECT UserId from users WHERE username = %s", [username])
    userID = cur.fetchone()['UserId']
    SuperviserName = form.SuperviserName.data
    SuperViserEMail = form.SuperviserEmail.data
    From = form.From.data
    To = form.To.data
    if request.method == 'POST':
        cur.execute(
            "INSERT INTO Bookings(SName, SEmail, fromDateTime, toDateTime, UserId, EquipID) Values(%s, %s, %s, %s, %s, %s)", 
        (SuperviserName, SuperViserEMail, From, To, userID, EquipId))
        mysql.connection.commit()
        flash("Booking Request Sent.")
        return redirect(url_for('dashboard'))

    result = cur.execute("SELECT Name FROM Equipments where id = %s", [EquipID])
    EquipName = cur.fetchone()['Name']
    cur.close()
    
    return render_template('book_slot.html', EquipName = EquipName, form=form)

if __name__ == '__main__':
    app.secret_key = "8Wy@d3E&wTin"
    app.run(debug=True)
