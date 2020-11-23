from itertools import chain
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, HiddenField
from wtforms.fields.html5 import DateTimeLocalField
from passlib.context import CryptContext
from functools import wraps
from wtforms import form

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

#Function to check user login status. Will throw error if unauthorized
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please log in.', 'danger')
            return redirect(url_for('login'))
    return wrap

#Function to check whether user has Administrative privileges. Will redirect other users to Home page
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and 'admin' in session:
            return f(*args, **kwargs)
        elif not 'logged_in' in session:
            flash('Unauthorized. Please login.', 'danger')
            return redirect(url_for('login'))
        else:
            flash('Unauthorized. Only for administrator.', 'danger')
            return redirect(url_for('index'))
    return wrap

#Flask Route for Home Page
@app.route('/')
def index():
    return render_template('home.html')

#Flask Route to view all users in Admin mode
@app.route('/users')
@is_admin
def users():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('users.html', users = users)
    flash("No users found.", "danger")
    return render_template('home.html')

#Flask form to Update Booking Status
class UpdateBooking(Form):
    typeList = [('Awaited', 'Awaited'), ('Accepted', 'Accepted'),('Rejected', 'Rejected')]
    status = SelectField('Status', choices=typeList)
    bookingID = HiddenField('ID')

#Flask Route to update slot booking requests
@app.route('/update_booking/<int:BookingID>', methods=['GET', 'POST'])
@is_admin
def update_booking(BookingID):
    form = UpdateBooking(request.form)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        Status = request.form['status']
        BookingID = request.form['bookingID']
        cur.execute("UPDATE Bookings SET RequestStatus= %s WHERE BookingID = %s", (Status, BookingID))
        mysql.connection.commit()
        cur.close()
        flash("Status Updated.", "success")
        return redirect(url_for('requests'))
    return render_template('update_booking.html', BookingID=BookingID, form=form)

#Flask form to Reschedule Booking
class RescheduleBooking(Form):
    From = DateTimeLocalField("From: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    To = DateTimeLocalField("To: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    bookingID = HiddenField('ID')

@app.route('/reschedule/<int:BookingID>', methods=['GET', 'POST'])
@is_admin
def reschedule(BookingID):
    form = RescheduleBooking(request.form)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        Status = 'Rescheduled'
        BookingID = request.form['bookingID']
        From = request.form['From']
        To = request.form['To']
        cur.execute("UPDATE Bookings SET RequestStatus= %s, fromDateTime=%s, toDateTime=%s WHERE BookingID = %s",(Status, From, To, BookingID))
        mysql.connection.commit()
        cur.close()
        flash("Booking Rescheduled.", "success")
        return redirect(url_for('requests'))
    return render_template('reschedule.html', BookingID=BookingID, form=form)

#Flask Route to view slot booking requests
@app.route('/requests', methods=['GET', 'POST'])
@is_admin
def requests():
    cur = mysql.connection.cursor()
    result = cur.execute(
        "SELECT e.Name as equipmentName,\
            u.name as userName,\
            b.UserId, b.fromDateTime, b.toDateTime,\
            b.SName, b.SEmail, b.BookingID from Bookings b\
            INNER JOIN users u on u.UserId = b.UserId\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.RequestStatus='Awaited'")
    requests = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('requests.html', requests = requests,form=form)
    flash("No Pending Requests.", "danger")
    return render_template('requests.html', form=form)

#Flask Route to view particular user ID and their history in Admin mode
@app.route('/user/<int:UserId>')
@is_admin
def user(UserId):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT username, name, accountType FROM users WHERE UserId = %s", [UserId])
    cur_user = cur.fetchone()
    result = cur.execute(
        "SELECT e.Name as equipmentName,\
            b.fromDateTime, b.toDateTime, b.RequestStatus,\
            b.SName, b.SEmail from Bookings b\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.UserId = %s", [UserId])
    history = cur.fetchall()
    cur.close()
    return render_template('user.html', history = history, user=cur_user)

#Form to register for the C4DFED slot booking facility
class RegisterForm(Form):
    typeList = [('Institute', 'Institute'), ('Academic', 'Academic'), ('Other','Other')]
    name = StringField('Name', [validators.Length(min=1, max=50), validators.DataRequired()])
    username = StringField('E-mail ID', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired(), validators.EqualTo('confirm', message='Passwords Do not match')])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    accountType = SelectField('Account Type', choices=typeList)

#Flask Route to register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = cryptcontext.hash(str(form.password.data))
        accountType = form.accountType.data
        
        #Create Cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        
        if(result == 0):
            cur.execute("INSERT INTO users(name, username, password, accountType) Values(%s, %s, %s, %s)", (name, username, password, accountType))
            mysql.connection.commit()
            flash("Registered Successfully", "success")
        #Raise error if email already used
        else:
            error = 'An account already exists with this email address.'
            return render_template('register.html', error= error, form=form)

        #Close Connection
        cur.close()

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

#Flask Route to login to C4DFED slot booking facility
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

            #Verify encrypted password
            if cryptcontext.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                if data['accountType'] == 'admin':
                    session['admin'] = True
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

#Flask route to logout of current session. Redirects to login page
@app.route('/logout')
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('login'))

#Flask route to view user dashboard with all available equipment for booking
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Equipments")
    users = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('dashboard.html', Equipments = users)
    flash("No Equipments available.", "danger")
    return render_template('home.html')

#flask route to view user profile with user history
@app.route('/profile')
@is_logged_in
def profile():
    username=session['username']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT UserId, username, name, accountType FROM users WHERE username = %s", [username])
    cur_user = cur.fetchone()
    UserId = cur_user['UserId']
    result = cur.execute(
        "SELECT e.Name as equipmentName,\
            b.fromDateTime, b.toDateTime, b.RequestStatus,\
            b.SName, b.SEmail from Bookings b\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.UserId = %s", [UserId])
    history = cur.fetchall()
    cur.close()
    return render_template('profile.html', history = history, user=cur_user)

#Form to record booking details of equipment with timings and supervisor details
class BookingForm(Form):
    SupervisorName = StringField('Supervisor Name', [validators.Length(min=1, max=255), validators.DataRequired()])
    SupervisorEmail = StringField('Supervisor Email', [validators.Length(min=1), validators.DataRequired()])
    From = DateTimeLocalField("From: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    To = DateTimeLocalField("To: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')

#Flask route to book slot of a particular equipment
@app.route('/book_slot/<int:EquipID>', methods=['GET', 'POST'])
@is_logged_in
def book_slot(EquipID):
    form = BookingForm(request.form)
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        From = form.From.data
        To = form.To.data
        username = session['username']
        result = cur.execute("SELECT UserId from users WHERE username = %s", [username])
        userID = cur.fetchone()['UserId']
        SupervisorName = form.SupervisorName.data
        SupervisorEMail = form.SupervisorEmail.data

        # TODO : Sanitize that the slot isn't already booked or awaited

        cur.execute(
            "INSERT INTO Bookings(SName, SEmail, fromDateTime, toDateTime, UserId, EquipID) Values(%s, %s, %s, %s, %s, %s)", 
        (SupervisorName, SupervisorEMail, From, To, userID, EquipID))
        mysql.connection.commit()
        cur.close()
        flash("Booking Request Sent.", "success")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT Name FROM Equipments where id = %s", [EquipID])
    EquipName = cur.fetchone()['Name']
    cur.close()
    
    return render_template('book_slot.html', EquipName = EquipName,EquipID = EquipID, form=form)

#Server runs on 127.0.0.1:5000
if __name__ == '__main__':
    app.secret_key = "8Wy@d3E&wTin"
    app.run(debug=True)
