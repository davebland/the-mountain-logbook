from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from pymongo import errors as mongo_errors
from datetime import datetime
from dotenv import load_dotenv
import os
import mongo_helpers as db
import email_notifications as mail
import asyncio
import csv


# APP SETUP
app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandombackupstring")

# MONGODB SETUP
# Get creds from enviroment variables if present other wise try env file (dev only)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MONGO_DBNAME'] = os.getenv('MONGO_DBNAME')
if not app.config['MONGO_URI'] or not app.config['MONGO_DBNAME']:
    print('Using dev mongo creds')
    load_dotenv()
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_DBNAME'] = os.getenv('MONGO_DBNAME')

mongo = PyMongo(app)

# ERROR HANDLERS

@app.errorhandler(mongo_errors.OperationFailure)
def handle_mongo_op_failure(e):
    """ Return 503 error with custom page """
    flash(e)
    return render_template('error.html'), 503

# ROUTE HELPER FUNCTIONS

def login_check():
    """ If user logged in return true otherwise false """
    if 'user_id' in session:
        return True
    return False

def get_entries(entry_id = None, user_id = None, area_id = None, page = 1):
    """ Get entries by page from DB according to priority entry_id, area_id, user_id """
    if entry_id:
        # Get a single entry
        return db.get_entry(entry_id)
    elif area_id and not user_id:
        # Get all entries for given area and page
        return db.get_entries_for_area(area_id)
    elif user_id and not area_id:
        # Get all entries for given user and page       
        return db.get_entries_for_user(user_id, page)
    elif user_id and area_id:
        # Get all entries for given user and given area
        return "YOU ARE REQUESTING entries FOR USER %s FOR AREA %s" % (user_id, area_id)
    else:
        return "ERROR - No entry_id, area_id or user_id supplied"

def areas_to_dict(cursor_object):
    """ Convert a cursor oject containing areas and ids to a dict """
    areas_dict = {}
    for record in cursor_object:
        areas_dict[str(record['_id'])] = record['name']  
    return areas_dict

# ROUTES (main)

@app.route('/')
@app.route('/<page>')
def index(page = 1):
    """ Main route returning app homepage or else login page """
    if login_check():        
        # Get user stats
        stats = db.get_user_stats(session['user_id'])
        # Check for request data and render home page with filter or without accordingly
        if request.args:
            return render_template('logbook-home.html', 
                                title="Logbook Home", 
                                user_stats=stats, 
                                user_entries=db.get_entries_for_user(session['user_id'], int(page), request.args),
                                area_list=areas_to_dict(db.get_areas()),
                                set_filters=request.args
                            )
        else:
            return render_template('logbook-home.html', 
                                title="Logbook Home", 
                                user_stats=stats, 
                                user_entries=db.get_entries_for_user(session['user_id'], int(page)), 
                                area_list=areas_to_dict(db.get_areas())
                            )

    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    """ Login a user by setting session and redirect to home """
    if 'login-email' in request.form:
        email = request.form['login-email'].lower()
        # Check if the user exists and set session to user id if so, send notification       
        if db.check_user(email):
            session["user_id"] = db.check_user(email)            
            asyncio.run(mail.send_login_notification(email))
            return redirect(url_for('index'))
        else:
            flash('Sorry, no user found with email %s' % email)
            return redirect(url_for('index'))
    else:
        flash('Sorry, login request invalid')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """" Logout a user by destroying session and redirect to home """
    session.clear()
    return redirect(url_for('index'))

# ROUTES (generate views)

@app.route('/new')
def new():
    """ Generate page for making of a new entry"""
    if login_check():
        return render_template('new-edit.html', title="New Entry", entry="", area_list=areas_to_dict(db.get_areas()))
    return redirect( url_for('index') )

@app.route('/edit/entry/<entry_id>')
def edit_entry(entry_id):
    """ Generate page to edit an existing entry"""
    if login_check():
        return render_template('new-edit.html', title="Edit Entry", entry=db.get_entry(entry_id), area_list=areas_to_dict(db.get_areas()))
    return redirect( url_for('index') )

@app.route('/edit/areas')
def edit_areas():
    """ Generate page to edit areas """
    if login_check():
        return render_template('edit-areas.html', title="Edit Areas", area_list=db.get_areas())
    return redirect( url_for('index') )

@app.route('/others')
def others():
    """ Generate page to view entries submitted by others """
    if login_check():
        return render_template('others.html', title="Other Users", area_list=db.get_areas())
    return redirect( url_for('index') )

# ROUTES (retrieve data)

@app.route('/get/entries', methods=['POST'])
def get():
    """ Return entries from DB according to entry_id, area_id or user_id in post data (return all fields) """
    if login_check():
        return get_entries(request.form['entry_id'], request.form['user_id'], request.form['area_id'])
    return redirect( url_for('index') )

@app.route('/get/areas')
def areas():
    """ Return dict of areas and id's """
    if login_check():
        areas_raw = db.get_areas()      
        area_dict = {}
        for area in areas_raw:
            area_dict[area['name']] = str(area['_id'])
        return area_dict
    return "Not logged in"

@app.route('/get/users')
def users():
    """ Return dict of users and id's """
    if login_check():
        users_raw = db.get_users()      
        users_dict = {}
        for user in users_raw:
            users_dict[str(user['_id'])] = user['display_name']
        return users_dict
    return "Not logged in"

@app.route('/export/<user_id>')
def export(user_id):
    """ Generate csv of user entries and return for download """
    user_entries = db.get_entries_for_user_for_export(user_id)
    area_dict = areas()
    # Invert dict so we can lookup by id
    area_dict = dict(map(reversed, area_dict.items()))
    # Create csv
    csv_name = "mountain-logbook-export-" + user_id + "-" + datetime.now().strftime("%d-%b-%Y") + ".csv"
    file_path = url_for('static', filename=csv_name)
    write_file_path = file_path.strip('/')
    with open(write_file_path, mode='w') as csv_file:        
        fieldnames = user_entries[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in user_entries:
            # Translate area id in each entry into an area name and the write to file
            entry['area_id'] = area_dict[entry['area_id']]
            csv_writer.writerow(entry)
    return redirect(file_path)

# ROUTES (create data)

@app.route('/create/<create_type>', methods=["POST"])
def create(create_type):
    """ Insert new data into DB """
    # If new user do not do login check
    if create_type == "user":
        # Check if user is already registered first otherwise add new user to db
        already_registered_user_id = db.check_user(request.form['signup-email'])
        if already_registered_user_id:
            flash('User %s already exists, please login instead' % request.form['signup-email'])
            return redirect( url_for('index') )           
        else:
            create_user_result = db.create_user(request.form)
            flash(create_user_result)
            # Log new user in by setting session
            session["user_id"] = db.check_user(request.form['signup-email'])
            return redirect( url_for('index') )
    elif login_check():
        # Connect to DB and add new entry or area according to type specified
        if create_type == "entry":
            create_update_result = db.create_update_entry(request.form)
            flash(create_update_result)
            return redirect( url_for('index') )
        elif create_type == "area":
            create_area_result = db.create_update_area(request.form)
            flash(create_area_result)
            # If reload requested in arguments this is a request from edit page rather than modal form
            if request.args.get('reload_page'):
                return redirect( url_for('edit_areas') )
            return create_area_result
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
            create_update_result = db.create_update_area(request.form, entity_id)
            flash(create_update_result)
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
            delete_result = db.delete_area(entity_id)
            flash(delete_result)
            return redirect( url_for('edit_areas') )
        else:
            return "DELETING ERROR - none or incorrect type supplied"
    return redirect( url_for('index') )

# Set flask parameters and run
if __name__ == '__main__':
    app.run(host=os.getenv('IP', "0.0.0.0"), port=int(os.getenv('PORT', "5000")), debug=True)