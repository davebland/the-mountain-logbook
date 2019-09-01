# DB HELPERS FOR MONGO

from app import mongo, session
from bson.objectid import ObjectId
from bson.json_util import dumps
from datetime import datetime
import math

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
        'signup_date' : datetime.strftime(ObjectId(user_id).generation_time, '%d %B %Y'),
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

def get_entries_for_user(user_id, page = 1, db_filter = {}):
    """ Return all entries for a given user id if any exist """
    print(db_filter)
    query = {'user_id':user_id}
    entries_per_page = 3
    entry_count =  mongo.db.entries.count_documents(query)
    max_pages = math.ceil(entry_count / entries_per_page)
    if entry_count:
        if max_pages == 1:
            # Get a single page of results
            page_of_entries = mongo.db.entries.find(query).limit(entries_per_page)
            return { 'entries' : page_of_entries, 'current_page': page}
        elif page == 1:
            # Get results for first page
            page_of_entries = mongo.db.entries.find({'user_id':user_id}).limit(entries_per_page)
            return { 'entries' : page_of_entries, 'current_page': page, 'next_page' : 2}
        elif page < max_pages:
            # Get results page by page
            page_of_entries = mongo.db.entries.find({'user_id':user_id}).skip((page-1)*entries_per_page).limit(entries_per_page)
            return { 'entries' : page_of_entries, 'current_page': page, 'previous_page' : page - 1, 'next_page' : page + 1}
        elif page == max_pages:
            # Get last page of results
            page_of_entries = mongo.db.entries.find({'user_id':user_id}).skip((page-1)*entries_per_page).limit(entries_per_page)
            return { 'entries' : page_of_entries, 'current_page': page, 'previous_page' : page - 1}
        else:
            return None
    else:
        return None

def get_entries_for_area(area_id):
    """ Get all entries for given area, regardless of user """
    area_entries_raw = mongo.db.entries.find({'area_id':area_id},{'_id':0})
    return dumps(area_entries_raw)

def get_entry(entry_id):
    """ Return all fields for specified log entry """
    entry_data = mongo.db.entries.find_one({'_id':ObjectId(entry_id)})
    entry_data['_id'] = str(entry_data['_id'])
    entry_data['date'] = datetime.strftime(entry_data['date'], "%d-%b-%Y")
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

# AREAS

def get_areas():
    """ Get all areas from DB """
    return mongo.db.areas.find()

def create_update_area(form_data, area_id = None):
    """ Create a new area in DB or update an existing one """    
    new_area = {
        'name' : form_data['name']
    }
    if area_id:
        # Update existing area
        mongo.db.areas.update_one({'_id':ObjectId(area_id)},{'$set': new_area})
        return "Area '%s' updated" % new_area['name']
    else:
        # Insert new area
        mongo.db.areas.insert_one(new_area)
        return "New area '%s' created" % new_area['name']

def delete_area(area_id):
    """ Delete an area from the DB """
    delete = mongo.db.areas.find_one_and_delete({'_id':ObjectId(area_id)})
    return "Area '%s' Deleted" % str(delete['name'])