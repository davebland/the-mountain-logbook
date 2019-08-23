# DB HELPERS FOR MONGO

from app import mongo
from bson.objectid import ObjectId

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
        'no_of_entries' : 123,
        'total_dist' : 456,
        'highest_peak' : 789
    }
    return user_stats

def get_entries_for_user(user_id):
    """ Return all entries for a given user id """
    user_entries = mongo.db.entries.find({'user_id':user_id})
    return user_entries