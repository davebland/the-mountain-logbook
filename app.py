from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from pymongo import errors as mongo_errors
import json # required for dev only
import os
import mongo_helpers as db
import email_notifications as mail
import asyncio

# APP SETUP
app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandombackupstring")

# MONGODB SETUP
# Get creds from enviroment variables if present other wise try untracked file (dev)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['MONGO_DBNAME'] = os.getenv('MONGO_DBNAME')

if not app.config['MONGO_URI'] or not app.config['MONGO_DBNAME']:
    print('Using local mongo creds')
    with open('mongo_creds.txt') as creds:
        data = json.load(creds)
        app.config['MONGO_DBNAME'] = data['MONGO_DBNAME']
        app.config['MONGO_URI'] = data['MONGO_URI']

mongo = PyMongo(app)

# Test route
@app.route('/db-test')
def db_test():
    return render_template('db-test.html', data_set=mongo.db.users.find())

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

def filter_entries(user_id, filter_args, page = 1):
    """ Filter the entries returned before rendering page """
    if filter_args['filter-min-date']:
        db_filter = "'date': {'$gt':'%s'}" % filter_args['filter-min-date']

    return db.get_entries_for_user(user_id, page, db_filter)

            
    print(all_entries['entries'])
    return get_entries("", session['user_id'], "", int(page))

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
        print(request.args)
        if request.args:
            return render_template('logbook-home.html', 
                                title="Logbook Home", 
                                user_stats=stats, 
                                user_entries=filter_entries(session['user_id'], request.args, int(page)),
                                area_list=areas_to_dict(db.get_areas())
                            )
        else:
            return render_template('logbook-home.html', 
                                title="Logbook Home", 
                                user_stats=stats, 
                                user_entries=get_entries("", session['user_id'], "", int(page)), 
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
        return render_template('new-edit.html', title="New Entry", entry="", area_list=db.get_areas())
    return redirect( url_for('index') )

@app.route('/edit/entry/<entry_id>')
def edit_entry(entry_id):
    """ Generate page to edit an existing entry"""
    if login_check():
        return render_template('new-edit.html', title="Edit Entry", entry=db.get_entry(entry_id), area_list=db.get_areas())
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
        return render_template('others.html', title="Others Page", area_list=db.get_areas())
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