import csv
import mongo_helpers as db

def export_entries_as_csv():
    """ Get all user entries and generate csv file """
    user_entries = db.get_entries_for_user_for_export('5d65442c79ba2dc9f24fca37')
    with open('temp.csv', mode='w') as csv_file:
        fieldnames = user_entries[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for entry in user_entries:
            csv_writer.writerow(entry)

export_entries_as_csv()