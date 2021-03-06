from itertools import chain
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, json
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, HiddenField
from wtforms.fields.html5 import DateTimeLocalField
from passlib.context import CryptContext
from functools import wraps
from wtforms import form
from config import config
import os

cryptcontext = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"]) # Schemes for encrypting passwords

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = config.MYSQL_CURSORCLASS
app.secret_key = os.urandom(12).hex()

# init MySQL
mysql = MySQL(app)

# init Mail
# Ensure 2 Factor Authentication is off and allow less secure app access
mail = Mail(app)

app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
mail = Mail(app)

def is_logged_in(f):
    """
    is_logged_in(f):
        Decorator to verify if the user is logged in to access the particular page.
        Redirects to login page otherwise.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please log in.', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    """
    is_admin(f):
        Decorator to verify if the user is logged in and has admin privileges.
        Redirects to login page if not logged in.
        Redirects to home page if not an admin.
    """
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

@app.route('/')
def index():
    """
    index(): Renders the home page.
    @route: '/'
    @privilege reqd: None
    """
    return render_template('home.html')

@app.route('/users')
@is_admin
def users():
    """
    users(): Renders the page with all registered users' details.
    @route: '/users'
    @privilege reqd: admin
    """
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('users.html', users = users)
    flash("No users found.", "danger")
    return render_template('home.html')

@app.route('/update_payment/<int:UserId>/<int:BookingID>', methods=['GET', 'POST'])
@is_admin
def update_payment(UserId, BookingID):
    """
    update_payment(BookingID): changes the payment status for the booking.
    @route: '/update_payment/<int:BookingID>'
    @privilege reqd: admin
    """
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Bookings SET Payment= %s WHERE BookingID = %s", (1, BookingID))
    mysql.connection.commit()
    cur.close()
    flash("Status Updated.", "success")
    return redirect('/user/' + str(UserId))

class UpdateBooking(Form):
    """
    UpdateBooking(Form): Form used by the admin to update the booking request.
    """
    typeList = [('Awaited', 'Awaited'), ('Accepted', 'Accepted'),('Rejected', 'Rejected')]
    status = SelectField('Status', choices=typeList)
    bookingID = HiddenField('ID')

@app.route('/update_booking/<int:BookingID>', methods=['GET', 'POST'])
@is_admin
def update_booking(BookingID):
    """
    update_booking(BookingID): Renders the update booking requests page.
    @route: '/update_booking/<int:BookingID>'
    @privilege reqd: admin
    """
    form = UpdateBooking(request.form)
    if request.method == 'POST':
        # POST Request : Perform action
        cur = mysql.connection.cursor()
        Status = request.form['status']
        BookingID = request.form['bookingID']
        cur.execute("UPDATE Bookings SET RequestStatus= %s WHERE BookingID = %s", (Status, BookingID))
        mysql.connection.commit()
        result = cur.execute(
            "SELECT e.Name as equipmentName,\
            u.name, u.username,\
            b.UserId, b.fromDateTime, b.toDateTime,\
            b.SName, b.SEmail from Bookings b\
            INNER JOIN users u on u.UserId = b.UserId\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.BookingID=%s",[BookingID])
        Data = cur.fetchone()
        name = Data['name']
        From = Data['fromDateTime']
        To = Data['toDateTime']
        EquipName = Data['equipmentName']
        SupervisorName = Data['SName']
        SupervisorEmail = Data['SEmail']
        UserEmail = Data['username']
        cur.close()
        msg = Message('C4DFED Slot Update',sender=app.config['MAIL_USERNAME'], recipients=[UserEmail])
        msg.body = "Hi {}\nYour booking for the following equipment at C4DFED -\nEquipment: {}\nFrom: {}\nTo: {}\n has been {} by the Admin of C4DFED and your Supervisor: {}.\nContact them for further details".format(name, EquipName, From, To,Status, SupervisorName)
        mail.send(msg)
        msg = Message('C4DFED Slot Update', sender=app.config['MAIL_USERNAME'],recipients=[SupervisorEmail])
        msg.body = "Hi {}\nYour Student: {}'s booking for the following equipment at C4DFED -\nEquipment: {}\nFrom: {}\nTo: {}\n has been {}.\nContact us for further details.".format(SupervisorName,name, EquipName, From, To, Status)
        mail.send(msg)
        flash("Status Updated.", "success")
        return redirect(url_for('requests'))
    # GET Request : Load the form
    return render_template('update_booking.html', BookingID=BookingID, form=form)

class RescheduleBooking(Form):
    """
    RescheduleBooking(Form): Form used by the admin to reschedule a booking request.
    """
    From = DateTimeLocalField("From: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    To = DateTimeLocalField("To: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    bookingID = HiddenField('ID')

@app.route('/reschedule/<int:BookingID>', methods=['GET', 'POST'])
@is_admin
def reschedule(BookingID):
    """
    reschedule(BookingID): Renders the reschedule booking requests page.
    @route: '/reschedule/<int:BookingID>'
    @privilege reqd: admin
    """
    form = RescheduleBooking(request.form)
    if request.method == 'POST':
        # POST Request : Perform action
        cur = mysql.connection.cursor()
        Status = 'Rescheduled'
        BookingID = request.form['bookingID']
        From = request.form['From']
        To = request.form['To']
        cur.execute("UPDATE Bookings SET RequestStatus= %s, fromDateTime=%s, toDateTime=%s WHERE BookingID = %s",(Status, From, To, BookingID))
        mysql.connection.commit()
        result = cur.execute(
            "SELECT e.Name as equipmentName,\
            u.name, u.username,\
            b.UserId, b.fromDateTime, b.toDateTime,\
            b.SName, b.SEmail from Bookings b\
            INNER JOIN users u on u.UserId = b.UserId\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.BookingID=%s", [BookingID])
        Data = cur.fetchone()
        name = Data['name']
        From = Data['fromDateTime']
        To = Data['toDateTime']
        EquipName = Data['equipmentName']
        SupervisorName = Data['SName']
        SupervisorEmail = Data['SEmail']
        UserEmail = Data['username']
        cur.close()
        msg = Message('C4DFED Slot Rescheduled',sender=app.config['MAIL_USERNAME'], recipients=[UserEmail])
        msg.body = "Hi {}\nYour booking for the following equipment at C4DFED -\nEquipment: {}\n has been rescheduled. Below are the new timings.\nFrom: {}\nTo: {}\nKindly visit your profile to accept/reject the proposed timings.".format(name, EquipName, From, To)
        mail.send(msg)
        msg = Message('C4DFED Slot Rescheduled',sender=app.config['MAIL_USERNAME'], recipients=[SupervisorEmail])
        msg.body = "Hi {}\nYour Student: {}'s booking for the following equipment at C4DFED -\nEquipment: {}\nhas been rescheduled. Below are the new timings.\nFrom: {}\nTo: {}\nContact us for further details.".format(SupervisorName, name, EquipName, From, To)
        mail.send(msg)
        flash("Booking Rescheduled.", "success")
        return redirect(url_for('requests'))
    # GET Request : Load the form
    return render_template('reschedule.html', BookingID=BookingID, form=form)


class AccRejRescheduling(Form):
    """
    AccRejReschedule(Form): Form for the user to accept/reject the rescheduled booking.
    """
    typeList = [('Accepted','Accept'), ('Rejected', 'Reject')]
    status = SelectField('Status', choices=typeList)
    bookingID = HiddenField('ID')

@app.route('/confirm_reschedule/<int:BookingID>', methods=['GET', 'POST'])
@is_logged_in
def confirm_resched(BookingID):
    """
    confirm_resched(BookingID): Renders the page for the user to Accept/Reject Rescheduled Booking.
    @route: '/confirm_reschedule/<int:BookingID>'
    @privilege reqd: log in
    """
    form = AccRejRescheduling(request.form)
    cur = mysql.connection.cursor()
    # Check if the booking belongs to logged in user

    result = cur.execute("SELECT u.username AS username, b.RequestStatus as RequestStatus \
            FROM Bookings b NATURAL JOIN users u WHERE BookingID = %s",[BookingID])
    if result == 1:
            booking = cur.fetchone()
            if booking['username'] == session['username'] and booking['RequestStatus'] == 'Rescheduled':
                # The username matches and the status is Rescheduled
                if request.method == 'POST':
                    # POST Request : Perform action
                    Status = request.form['status']
                    cur.execute("UPDATE Bookings SET RequestStatus= %s WHERE BookingID = %s",(Status, BookingID))
                    mysql.connection.commit()
                    result = cur.execute(
                                    "SELECT e.Name as equipmentName,\
                                    u.name, u.username,\
                                    b.UserId, b.fromDateTime, b.toDateTime,\
                                    b.SName, b.SEmail from Bookings b\
                                    INNER JOIN users u on u.UserId = b.UserId\
                                    INNER JOIN Equipments e\
                                    ON e.id = b.EquipID WHERE b.BookingID=%s", [BookingID])
                    Data = cur.fetchone()
                    name = Data['name']
                    From = Data['fromDateTime']
                    To = Data['toDateTime']
                    EquipName = Data['equipmentName']
                    SupervisorName = Data['SName']
                    SupervisorEmail = Data['SEmail']
                    UserEmail = Data['username']
                    cur.close()
                    msg = Message('C4DFED Slot Update',sender=app.config['MAIL_USERNAME'], recipients=[UserEmail])
                    msg.body = "Hi {}\nYour booking for the following equipment at C4DFED -\nEquipment: {}\nFrom: {}\nTo: {}\n has been {} by the Admin of C4DFED and your Supervisor: {}.\nContact them for further details".format(name, EquipName, From, To,Status, SupervisorName)
                    mail.send(msg)
                    msg = Message('C4DFED Slot Update', sender=app.config['MAIL_USERNAME'],recipients=[SupervisorEmail])
                    msg.body = "Hi {}\nYour Student: {}'s booking for the following equipment at C4DFED -\nEquipment: {}\nFrom: {}\nTo: {}\n has been {}.\nContact us for further details.".format(SupervisorName,name, EquipName, From, To, Status)
                    mail.send(msg)
                    flash("Accepted/Rejected Rescheduling.", "success")
                    return redirect(url_for('profile'))
                # GET Request : Load the form
                cur.close()
                return render_template('confirm_rescheduling.html', BookingID=BookingID, form=form)
    cur.close()
    flash("Unauthorized Rescheduling.", "danger")
    return redirect(url_for('profile'))

@app.route('/requests', methods=['GET', 'POST'])
@is_admin
def requests():
    """
    requests(): Renders the awaiting requests page.
    @route: '/requests'
    @privilege reqd: admin
    """
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

def computeOutstandingAmount(bookings):
    amount = 0.0
    for i in bookings:
        if i['RequestStatus'] == 'Accepted' and i['Payment'] == 0:
            amount += float(i['cost'])
    return amount

@app.route('/user/<int:UserId>')
@is_admin
def user(UserId):
    """
    user(UserID): Renders a particular user's history.
    @route: '/user/<int:UserId>'
    @privilege reqd: admin
    """
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT username, name, accountType, UserId FROM users WHERE UserId = %s", [UserId])
    cur_user = cur.fetchone()
    costColumns = {'Institute': 'CostInstitute' , 'Other': 'CostOther','Academic': 'CostAcademic', 'admin': 'CostInstitute'}
    result = cur.execute(
        "SELECT e.Name as equipmentName,\
            b.fromDateTime, b.toDateTime, b.RequestStatus,\
            b.SName, b.SEmail, b.Payment, b.BookingID, e." + costColumns[cur_user['accountType']] + " AS cost from Bookings b\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.UserId = %s", [UserId])
    history = cur.fetchall()
    cur.close()
    return render_template('user.html', history = history, user=cur_user, amount = computeOutstandingAmount(history))

class RegisterForm(Form):
    """
    RegisterForm(Form): Form for a new user to register.
    """
    typeList = [('Institute', 'Institute'), ('Academic', 'Academic'), ('Other','Other')]
    name = StringField('Name', [validators.Length(min=1, max=50), validators.DataRequired()])
    username = StringField('E-mail ID', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6, max=50), validators.DataRequired(), validators.EqualTo('confirm', message='Passwords Do not match')])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    accountType = SelectField('Account Type', choices=typeList)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    register(): Renders the registration form for new users.
    @route: '/register'
    @privilege reqd: None
    """
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = cryptcontext.hash(str(form.password.data))
        accountType = form.accountType.data
        
        # Create Cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        
        if(result == 0):
            cur.execute("INSERT INTO users(name, username, password, accountType) Values(%s, %s, %s, %s)", (name, username, password, accountType))
            mysql.connection.commit()
            flash("Registered Successfully", "success")
            msg = Message('C4DFED Account', sender=app.config['MAIL_USERNAME'],recipients=[username])
            msg.body = "Hi {}\nWelcome to C4DFED Equipment Slot Booking Facility.\nYou have successfully created an {} account. You can now book a slot for your research purposes.\nEnjoy your visit!".format(name,accountType)
            mail.send(msg)
        # Raise error if email already used
        else:
            error = 'An account already exists with this email address.'
            return render_template('register.html', error= error, form=form)

        # Close Connection
        cur.close()

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login(): Render the login form page.
    @route: '/login'
    @privilege reqd: None
    """
    if request.method == 'POST':
        # POST Request : Perform action
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users where username = %s", [username])
        if result>0:
            data = cur.fetchone()
            password = data['password']

            # Verify encrypted password
            if cryptcontext.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                if data['accountType'] == 'admin':
                    session['admin'] = True
                flash("You are now logged in", 'success')
                return redirect(url_for('dashboard'))
            else:
                # Wrong password
                error = 'Invalid Login'
                return render_template('login.html', error= error)
        else:
            # No user found
            error = 'Invalid Login'
            return render_template('login.html', error= error)
        cur.close()
    # GET Request : Load the form
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    logout(): Redirects to the login page after logging out of the current session.
    @route: '/logout'
    @privilege reqd: None
    """
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    """
    dashboard(): Renders a page with a list of facilities/ eqipments available in the C4DFED lab.
    @route: '/dashboard'
    @privilege reqd: log in
    """
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Equipments")
    users = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('dashboard.html', Equipments = users)
    # No equipments in the database
    flash("No Equipments available.", "danger")
    return render_template('home.html')

@app.route('/profile')
@is_logged_in
def profile():
    """
    profile(): Renders personal information of a user, his request status, bill summary, etc.
    @route: '/profile'
    @privilege reqd: log in
    """
    username=session['username']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT UserId, username, name, accountType FROM users WHERE username = %s", [username])
    cur_user = cur.fetchone()
    costColumns = {'Institute': 'CostInstitute' , 'Other': 'CostOther','Academic': 'CostAcademic', 'admin': 'CostInstitute'}
    UserId = cur_user['UserId']
    result = cur.execute(
        "SELECT e.Name as equipmentName,\
            b.fromDateTime, b.toDateTime, b.RequestStatus,\
            b.SName, b.SEmail, b.BookingID, b.Payment, e." + costColumns[cur_user['accountType']] + " AS cost from Bookings b\
            INNER JOIN Equipments e\
            ON e.id = b.EquipID WHERE b.UserId = %s", [UserId])
    history = cur.fetchall()
    cur.close()
    return render_template('profile.html', history = history, user=cur_user, amount = computeOutstandingAmount(history))

class BookingForm(Form):
    """
    BookingForm(Form): Form used by the user to send a booking request.
    """
    SupervisorName = StringField('Supervisor Name', [validators.Length(min=1, max=255), validators.DataRequired()])
    SupervisorEmail = StringField('Supervisor Email', [validators.Length(min=1), validators.DataRequired()])
    From = DateTimeLocalField("From: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')
    To = DateTimeLocalField("To: ", [validators.DataRequired()], format='%Y-%m-%dT%H:%M')

@app.route('/book_slot/<int:EquipID>', methods=['GET', 'POST'])
@is_logged_in
def book_slot(EquipID):
    """
    book_slot(): To send a booking request to the admin for a particlular equipment.
    @route: '/book_slot'
    @privilege reqd: log in
    """
    form = BookingForm(request.form)
    if request.method == 'POST':
        # POST Request : Perform action
        cur = mysql.connection.cursor()
        From = form.From.data
        To = form.To.data
        username = session['username']
        result = cur.execute("SELECT UserId, name from users WHERE username = %s", [username])
        curr_User = cur.fetchone()
        userID = curr_User['UserId']
        name = curr_User['name']
        SupervisorName = form.SupervisorName.data
        SupervisorEMail = form.SupervisorEmail.data

        cur.execute(
            "INSERT INTO Bookings(SName, SEmail, fromDateTime, toDateTime, UserId, EquipID) Values(%s, %s, %s, %s, %s, %s)", 
        (SupervisorName, SupervisorEMail, From, To, userID, EquipID))
        result = cur.execute("SELECT Name FROM Equipments where id = %s", [EquipID])
        cur_Equi = cur.fetchone()
        EquipName = cur_Equi['Name']
        mysql.connection.commit()
        cur.close()
        flash("Booking Request Sent.", "success")
        msg = Message('C4DFED Slot Booking',sender=app.config['MAIL_USERNAME'], recipients=[username])
        msg.body = "Hi {}\nYour booking for the following equipment at C4DFED -\nEquipment: {}\nFrom: {}To: {}\n has been recorded and is under purview by the Admin of C4DFED and your Supervisor: {}.\nYou will be notified of the booking status.".format(name, EquipName, From, To, SupervisorName)
        mail.send(msg)
        msg = Message('C4DFED Slot Booking', sender=app.config['MAIL_USERNAME'],recipients=[SupervisorEMail])
        msg.body = "Hi {}\nYour student has sent a booking request for the following equipment at C4DFED.\nName: {}\nEquipment: {}\nFrom: {}\nTo: {}\nKindly review the booking.".format(SupervisorName,name,EquipName,From,To)
        mail.send(msg)
        return redirect(url_for('dashboard'))
    # GET Request : Load the form after fetching the required data
    cur = mysql.connection.cursor()
    username = session['username']
    result = cur.execute("SELECT accountType from users WHERE username = %s", [username])
    ACCType = 'Cost'+cur.fetchone()['accountType']
    cur.close()
    if ACCType=='Costadmin':
        Cost = '0'
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT Name FROM Equipments where id = %s", [EquipID])
        cur_Equi = cur.fetchone()
        EquipName = cur_Equi['Name']
        cur.close()
    else:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT Name, CostInstitute, CostAcademic, CostOther FROM Equipments where id = %s", [EquipID])
        cur_Equi = cur.fetchone()
        EquipName = cur_Equi['Name']
        Cost=cur_Equi[ACCType]
        cur.close()
    
    return render_template('book_slot.html', EquipName = EquipName,EquipID = EquipID, form=form, Cost=Cost)

@app.route('/calendar')
@is_logged_in
def calendar():
    """
    Render fullcalendar.
    Courtesy https://github.com/kkarimi/flask-fullcalendar 
    """
    return render_template("json.html")

@app.route('/data')
@is_logged_in
def return_data():
    """
    Return json of calendar events.
    """
    cur = mysql.connection.cursor()
    result = cur.execute(
        "SELECT u.username AS username, e.Name AS EqName, DATE_FORMAT(b.fromDateTime, '%Y-%m-%dT%H:%i')\
            AS FromDateTime, DATE_FORMAT(b.toDateTime, '%Y-%m-%dT%H:%i') AS ToDateTime \
                FROM (Bookings b INNER JOIN Equipments e ON b.EquipID = e.id) INNER JOIN users u \
                    ON b.UserId = u.UserId WHERE b.RequestStatus = 'Accepted'")
    calendarEvents = cur.fetchall()
    eventList = []
    
    if 'admin' in session:
        # Admin can see the calendar along with the who booked it
        for e in calendarEvents:
            eventList.append({
                "title": e['EqName'] + ": " + e['username'],
                "start": e['FromDateTime'],
                "end": e['ToDateTime']
        })
    elif 'logged_in' in session:
        # Users can only see the calendar and not the user who booked it
        for e in calendarEvents:
            eventList.append({
                "title": e['EqName'],
                "start": e['FromDateTime'],
                "end": e['ToDateTime']
            })

    cur.close()
    # Convert Python List to JSON String
    jsonStr = json.dumps(eventList)
    return jsonStr

# Server runs on 127.0.0.1:5000
if __name__ == '__main__':
    app.run(debug=True) # debug = False for production
