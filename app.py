from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import json # required for dev only
import os
import mongo_helpers as db

# APP SETUP
app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandomstring")

# MONGODB SETUP
# Get creds from untracked file for dev purposes
with open('mongo_creds.txt') as creds:
    data = json.load(creds)
    app.config['MONGO_DBNAME'] = data['MONGO_DBNAME']
    app.config['MONGO_URI'] = data['MONGO_URI']

mongo = PyMongo(app)

# Test route
@app.route('/db-test')
def db_test():
    return render_template('db-test.html', data_set=mongo.db.users.find())

# ROUTE HELPER FUNCTIONS

def login_check():
    """ If user logged in return true otherwise false """
    if 'user_id' in session:
        return True
    return False

def get_entries(entry_id = None, user_id = None, area_id = None):
    """ Get entries from DB according to priority entry_id, area_id, user_id """
    if entry_id:
        # Get a single entry
        return db.get_entry(entry_id)
    elif area_id and not user_id:
        # Get all entries for given area
        return "YOU ARE REQUESTING entries FOR AREA %s" % area_id
    elif user_id and not area_id:
        # Get all entries for given user
        return db.get_entries_for_user(user_id)
    elif user_id and area_id:
        # Get all entries for given user and given area
        return "YOU ARE REQUESTING entries FOR USER %s FOR AREA %s" % (user_id, area_id)
    else:
        return "ERROR - No entry_id, area_id or user_id supplied"

def get_areas():
    """ Connect to DB and return dict containing all area ids and names """
    test_data = ({'area_id' : 'testarea1_id', 'area_name' : 'testarea1_name'}, {'area_id' : 'testarea2_id', 'area_name' : 'testarea2_name'}, {'area_id' : 'testarea3_id', 'area_name' : 'testarea3_name'})
    return test_data

# ROUTES (main)

@app.route('/')
def index():
    """ Main route returning app homepage or else login page """
    if login_check():
        # Get user stats
        stats = db.get_user_stats(session['user_id'])
        # Get entryset for user if any exist, otherwise return no entryflash
        entry_set = get_entries("", session['user_id'], "")
        if entry_set:
            return render_template('logbook-home.html', title="Logbook Home", user_stats=stats, user_entries=entry_set)
        else:
            flash('No entries found')
            return render_template('logbook-home.html', title="Logbook Home", user_stats=stats)

    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    """ Login a user by setting session and redirect to home """
    if 'login-email' in request.form:
        email = request.form['login-email']
        # Check if the user exists and set session to user id if so        
        if db.check_user(email):
            session["user_id"] = db.check_user(email)
            return redirect(url_for('index'))
        else:
            flash('Sorry, no user found with email %s' % email)
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
    """ Generate page for entry of a new entry"""
    if login_check():
        return render_template('new-edit.html', title="New entry", entry="", area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/edit/entry/<entry_id>')
def edit_entry(entry_id):
    """ Generate page to edit an existing entry"""
    if login_check():
        return render_template('new-edit.html', title="Edit entry", entry=db.get_entry(entry_id), area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/edit/areas')
def edit_areas():
    """ Generate page to edit areas """
    if login_check():
        return render_template('edit-areas.html', title="Edit Areas", area_list=get_areas())
    return redirect( url_for('index') )

@app.route('/others')
def others():
    """ Generate page to view entries submitted by others """
    if login_check():
        return render_template('others.html', title="Others Page", area_list=get_areas())
    return redirect( url_for('index') )

# ROUTES (retrieve data)

@app.route('/get/entries', methods=['POST'])
def get():
    """ Return entries from DB according to entry_id, area_id or user_id in post data (return all fields) """
    if login_check():
        return get_entries(request.form['entry_id'], request.form['user_id'], request.form['area_id'])
    return redirect( url_for('index') )

# ROUTES (create data)

@app.route('/create/<create_type>', methods=["POST"])
def create(create_type):
    """ Insert new data into DB """
    if login_check():
        # Connect to DB and add new user, entry or area according to type specified
        if create_type == "user":
            return "CREATING A USER"
        elif create_type == "entry":
            create_update_result = db.create_update_entry(request.form)
            flash(create_update_result)
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
        # Connect to DB and update entity_id of user, entryor area according to type specified
        if update_type == "user":
            return "UPDATING A USER %s " % entity_id
        elif update_type == "entry":
            create_update_result = db.create_update_entry(request.form, entity_id)
            flash(create_update_result)
            return redirect( url_for('index') )
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
        # Connect to DB and delete user, entryor area with entity_id according to type specified
        if delete_type == "user":
            return "DELETING A USER %s " % entity_id
        elif delete_type == "entry":
            delete_result = db.delete_entry(entity_id)
            flash(delete_result)
            return redirect( url_for('index') )
        elif delete_type == "area":
            return "DELETING AN AREA %s " % entity_id
        else:
            return "DELETING ERROR - none or incorrect type supplied"
    return redirect( url_for('index') )

# Set flask parameters
if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True)