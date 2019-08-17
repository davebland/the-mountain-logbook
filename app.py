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

def get_records(record_id = None, user_id = None, area_id = None):
    """ Get records from DB according to priority record_id, area_id, user_id """
    if record_id:
        # Get a single record
        return "YOU ARE REQUESTING RECORD %s" % record_id
    elif area_id and not user_id:
        # Get all records for given area
        return "YOU ARE REQUESTING RECORDS FOR AREA %s" % area_id
    elif user_id and not area_id:
        # Get all records for given user
        return "YOU ARE REQUESTING RECORDS FOR USER %s" % user_id
    elif user_id and area_id:
        # Get all records for given user and given area
        return "YOU ARE REQUESTING RECORDS FOR USER %s FOR AREA %s" % (user_id, area_id)
    else:
        return "ERROR - No record_id, area_id or user_id supplied"

def get_areas():
    """ Connect to DB and return dict containing all area ids and names """
    test_data = ({'area_id' : 'testarea1_id', 'area_name' : 'testarea1_name'}, {'area_id' : 'testarea2_id', 'area_name' : 'testarea2_name'}, {'area_id' : 'testarea3_id', 'area_name' : 'testarea3_name'})
    return test_data

# ROUTES (main)

@app.route('/')
def index():
    """ Main route returning app homepage or else login page """
    if login_check():
        # Get record set for user if any exist, otherwise return no record flash
        record_set = get_records("", 123, 456)
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

# ROUTES (generate views)

@app.route('/new')
def new():
    """ Generate page for entry of a new record """
    if login_check():
        return render_template('new-edit.html', title="New record", area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/edit/record/<record_id>')
def edit_record(record_id):
    """ Generate page to edit an existing record """
    if login_check():
        return render_template('new-edit.html', title="Edit record", record=record_id, area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/edit/areas')
def edit_areas():
    """ Generate page to edit areas """
    if login_check():
        return render_template('edit-areas.html', title="Edit Areas", area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/others')
def others():
    """ Generate page to view records submitted by others """
    if login_check():
        return render_template('others.html', title="Others Page", area_list=get_areas())
    return redirect( url_for('index') )

# ROUTES (retrieve data)

@app.route('/get/records', methods=['POST'])
def get():
    """ Return records from DB according to record_id, area_id or user_id in post data (return all fields) """
    if login_check():
        return get_records(request.form['record_id'], request.form['user_id'], request.form['area_id'])
    return redirect( url_for('index') )

# ROUTES (create data)

@app.route('/create/<create_type>', methods=["POST"])
def create(create_type):
    """ Insert new data into DB """
    if login_check():
        # Connect to DB and add new user, record or area according to type specified
        if create_type == "user":
            return "CREATING A USER"
        elif create_type == "record":
            flash("CREATING A RECORD: {}".format(request.form))
            return redirect( url_for('index') )
        elif create_type == "area":
            # If reload requested in arguments this is a request from edit page rather than modal form
            if request.args.get('reload_page'):
                flash("CREATING AN AREA: {}".format(request.form))
                return redirect( url_for('edit_areas') )
            return "CREATING AN AREA"
        else:
            return "CREATING ERROR - none or incorrect type supplied"
    return redirect( url_for('index') )

# ROUTES (update data)

@app.route('/update/<update_type>/<entity_id>', methods=["POST"])
def update(update_type, entity_id):
    """ Update existing data in DB """
    if login_check():
        # Connect to DB and update entity_id of user, record or area according to type specified
        if update_type == "user":
            return "UPDATING A USER %s " % entity_id
        elif update_type == "record":
            return "UPDATING A RECORD %s " % entity_id
        elif update_type == "area":
            flash("UPDATING AN AREA %s " % entity_id)
            return redirect( url_for('edit_areas') )
        else:
            return "UPDATING ERROR - none or incorrect type supplied"
    return redirect( url_for('index') )

# ROUTES (delete data)

@app.route('/delete/<delete_type>/<entity_id>')
def delete(delete_type, entity_id):
    """ Delete data in DB """
    if login_check():
        # Connect to DB and delete user, record or area with entity_id according to type specified
        if delete_type == "user":
            return "DELETING A USER %s " % entity_id
        elif delete_type == "record":
            return "DELETING A RECORD %s " % entity_id
        elif delete_type == "area":
            return "DELETING AN AREA %s " % entity_id
        else:
            return "DELETING ERROR - none or incorrect type supplied"
    return redirect( url_for('index') )

# Set flask parameters
if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True)