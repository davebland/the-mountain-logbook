from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandomstring")

# ROUTE HELPER FUNCTIONS

def login_check():
    """ If user logged in return true otherwise false """
    if 'user_id' in session:
        return True
    return False

# ROUTES

@app.route('/')
def index():
    """ Main route returning app homepage or else login page """
    if login_check():
        # Get record set for user if any exist, otherwise return no record flash
        record_set = "RECORDS FROM DB"
        if record_set:
            return render_template('logbook-home.html', title="Logbook Home", user_records=record_set)
        else:
            flash('No records found')
            return render_template('logbook-home.html', title="Logbook Home")

    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    """ Login a user by setting session and redirect to home """
    if 'login-email' in request.form:
        # Set email as user_id in session
        session["user_id"] = request.form['login-email']
        return redirect(url_for('index'))
    elif 'signup-email' in request.form:
        # Set email as user_id in session
        session["user_id"] = request.form['signup-email']
        return redirect(url_for('index'))
    return 'INVALID LOGIN'

@app.route('/logout')
def logout():
    """" Logout a user by destroying session and redirect to home """
    session.clear()
    return redirect(url_for('index'))

@app.route('/get/<record_id>')
def get(record_id):
    """ Get a record and return all fields """
    if login_check():
        return "YOUR REQUESTED: %s" % record_id
    return redirect( url_for('index') )

@app.route('/new')
def new():
    """ Generate page for entry of a new record """
    if login_check():
        return render_template('new-edit.html', title="New record")
    return redirect( url_for('index') )

@app.route('/add', methods=["POST"])
def add():
    """ Add a new record to DB """
    if login_check():
        # Connect to DB and add record
        return request.form
    return redirect( url_for('index') )

@app.route('/edit/<record_id>')
def edit(record_id):
    """ Generate page to edit an existing record """
    if login_check():
        return render_template('new-edit.html', title="Edit record", record=record_id)
    return redirect( url_for('index') )

@app.route('/update/<record_id>', methods=["POST"])
def update(record_id):
    """ Update an existing record in DB """
    if login_check():
        # Connect to DB and update record
        return "UPDATING " + request.form
    return redirect( url_for('index') )

@app.route('/delete/<record_id>', methods=["POST"])
def delete(record_id):
    """ Delete an existing record in DB """
    if login_check():
        # Connect to DB and delete record
        return "DELETING " + record_id
    return redirect( url_for('index') )

@app.route('/others')
def others():
    """ Generate page to view records submitted by others """
    if login_check():
        return render_template('others.html')
    return redirect( url_for('index') )

@app.route('/get/area', methods=["POST"])
def get_by_area():
    """ Return all records from DB for given area """
    if login_check():
        # Connect to DB and get records
        return request.form
    return redirect( url_for('index') )


# Set flask parameters
if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True)