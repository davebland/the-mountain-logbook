# DB HELPERS FOR MONGO

from app import mongo, session
from bson.objectid import ObjectId
from datetime import datetime

# USERS

def check_user(email):
    """ Check if a given user email exists in DB and return user id if so """
    user = mongo.db.users.find_one({'email':email})    
    if user:
        return str(user['_id'])
    return None

def get_user_stats(user_id):
    """ Generate user stats for given id """
    user_data = mongo.db.users.find_one({'_id':ObjectId(user_id)})
    user_stats = {
        'display_name' : user_data['display_name'],
        'signup_date' : ObjectId(user_id).generation_time,
        'no_of_entries' : mongo.db.entries.count_documents({'user_id':user_id}),
        'total_dist' : 456,
        'highest_peak' : 789
    }
    return user_stats

def create_user(form_data):
    """ Create a new user from form data and return user data """
    new_user = {
        'email' : form_data['signup-email'],
        'display_name' : form_data['display-name'],
        'share' : True
    }
    mongo.db.users.insert_one(new_user)    
    return "Thanks for signing up, we hope you enjoy using this application"

# ENTRIES

def get_entries_for_user(user_id):
    """ Return all entries for a given user id if any exist """
    if mongo.db.entries.count_documents({'user_id':user_id}):
        return mongo.db.entries.find({'user_id':user_id})
    else: 
        return None

def get_entry(entry_id):
    """ Return all fields for specified log entry """
    entry_data = mongo.db.entries.find_one({'_id':ObjectId(entry_id)})
    entry_data['_id'] = str(entry_data['_id'])
    entry_data['date'] = datetime.strftime(entry_data['date'], '%Y-%m-%d')
    return entry_data

def create_update_entry(form_data, entry_id = None):
    """ Use form data to update existing or insert new entry into DB """
    # Sanitise data first
    def to_float(string):
        """ Convert string to float if possible otherwise return none """
        if string:
            return float(string)
        else:
            return None
    new_entry = {
        'user_id' : session['user_id'],
        'name' : form_data['name'],
        'date' : datetime.strptime(form_data['date'], '%Y-%m-%d'),
        'area_id' : form_data['area_id'],
        'primary_terrain' : form_data['primary_terrain'],
        'duration' : int(form_data['duration']),
        'distance' : to_float(form_data['distance']),
        'highest_point_name' : form_data['highest_point_name'],
        'highest_point_os_grid' : form_data['highest_point_os_grid'],
        'highest_point_os_eastings' : to_float(form_data['highest_point_os_eastings']),
        'highest_point_os_northings' : to_float(form_data['highest_point_os_northings']),
        'highest_point_latitude' : to_float(form_data['highest_point_latitude']),
        'highest_point_longitude' : to_float(form_data['highest_point_longitude']),
        'additional_summits' : form_data['additional_summits'],
        'weather' : form_data['weather'],
        'participation' : form_data['participation'],
        'group_members' : form_data['group_members'],
        'notes' : form_data['notes']
    }
    if entry_id:
        # Update existing entry
        mongo.db.entries.update_one({'_id':ObjectId(entry_id)},{'$set': new_entry})
        return "Entry '%s' updated" % new_entry['name']
    else:
        # Insert new entry
        mongo.db.entries.insert_one(new_entry)
        return "New entry '%s' created" % new_entry['name']

def delete_entry(entry_id):
    """ Delete an entry from the DB """
    delete = mongo.db.entries.find_one_and_delete({'_id':ObjectId(entry_id)})
    return "Entry '%s' Deleted" % str(delete['name'])