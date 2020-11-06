from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField, SelectField
from passlib.context import CryptContext
from functools import wraps
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
    return render_template('home.html')

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
        cur.execute("INSERT INTO users(name, username, password, accountType) Values(%s, %s, %s, %s)", (name, username, password, accountType))
        mysql.connection.commit()

        #Close Connection
        cur.close()

        flash("Registered Successfully", "success")
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
    result = cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', users = users)
    else:
        msg = "No Users Found"
        return render_template('dashboard.html', msg = msg)
    cur.close()

class BookingForm(Form):
    SuperviserName = StringField('Superviser Name', [validators.Length(min=1, max=255), validators.DataRequired()])
    SuperviserEmail = StringField('Superviser Email', [validators.Length(min=1), validators.DataRequired()])
    date = DateField(id='datepick')

@app.route('/book_slot', methods=['GET', 'POST'])
@is_logged_in
def add_booking():
    form = BookingForm(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT Name FROM Equipments")
    Equipments = cur.fetchall()
    return render_template('book_slot.html', form=form, Equipments = Equipments)

if __name__ == '__main__':
    app.secret_key = "8Wy@d3E&wTin"
    app.run(debug=True)
