# The Mountain Logbook

## An online tool for logging mountain or hill walking experiences. Replicates, and improves on, a traditional paper logbook.

A 'Data Centric Development' milestone project for Code Institute.

The Mountain Logbook Online is a tool for recording details of mountain walking experiences. The essential user requirement is to be able to record and store details of any number of walk/hike/climbs that the user has completed. In essence, a digital logbook with which an individual can keep a record of their experience for personal interest and/or for the purposes of gathering evidence for qualification. There is an export functionality so the complete 'logbook' can be submitted to an awarding body for assessment.

A Python website using the Flask framework with MongoDB datastore.

## Demo
See http://the-mountain-logbook.herokuapp.com/

![Screenshot](static/images/screenshot.jpg?)
## UX
The application is primarily for people who will already be keeping a logbook of some kind, likely either paper based or spreadsheet. For this reason, the user interface will use a table layout as this will be familiar and should aid user take-up.
### User Stories
1. On first opening the application the user can either login to an existing account using an email address or create a new account by supplying a unique email address and display name.
2. It will not be possible to create accounts with duplicate email addresses and users will get clear feedback if an email address already exists.
3. Once logged in it will be obvious how to add a new entry.
4. Existing entries will be clearly displayed and can be filtered by date or area.
5. Existing entries can be amended or deleted by the user.
6. User will see basic statistics for their account including no. of entries, total hours walking and total distance travelled.
7. Entries will be categorized by area and users will be able to add, update and delete areas without affecting data in previously created records.
8. There will be a ‘others’ page where users can view selected information from other users’ entries on a per area basis.

## Features
- Basic user authentication by email and subsequent checking of valid session before returning data
- Responsive design for mobile or desktop
- ‘Member since’ derived from timestamp in Mongo ObjectId
- Pagination and filtering of entries on home page
- Basic handling of errors with custom error page
- Ajax calls to populate ‘entry details’ modal according to entry selected in table and without reloading page
- Ajax calls to populate ‘others’ table without reloading page
- Ability to add new areas during creation or update of an entry
- Feedback of create/update/delete actions via alert areas on each page
- Export to csv function via Python csv library
- Basic email notifications to admin using AWS SES smtp services

## Future Additions
- Richer user management including profile and update/delete controls
- Directly connect to 'Mountain-Training.org' (UK governing body) website for import into their CMS for candidate assessment
- 'Share' switch to give users controls over whether their entries are shared with other users or not
- More advanced search and filter controls for entries
- Export to csv according to filters selected
- Pre-dictated highest points (e.g. mountain summits) that users can select
- Mapping of summits and dates via Google Maps API or similar
- More advanced interactions with other users including linking of entries with other users in the system
- Record waypoint coordinates and map these
- Stats for each area on mountain area page plus a more graphical and data rich display.

## Technologies
- HTML5
- CSS3
- JavaScript
- Python
    - Flask 1.1.1 and associated dependencies
    - dnspython 1.16 and flask-pymongo 2.3.0
- Front End Libraries
    - JQuery 3.4.1
    - Bootstrap 4.3.1
    - Google Material Icons - https://material.io/resources/icons
- MongoDB
    - Cloud hosted on MongoDB Atlas

## Testing
The testing process was continuous throughout development. Built and tested in the following broad stages:
1. Basic flask app using template pages with initial layout
2. Constructed Python logic for moving data about via routes and views
3. Connected to MongoDB to test working with real data
4. Finalised styling and layout
5. Deployed to Heroku (initial development on local machine with virtualenv)
6. Extensive testing via front end, checking all features and clearing any bugs

Tested on different browsers and for desktop/mobile screen sizes via browser dev tools. CSS and HTML validated using online tools. Python code tested by building each function as a 'mini project' and testing the functionality and error handling before moving onto the next piece of functionality.
### User Story Testing
Tested the functionality of each story from a user point of view. Asked several other people to use the application without instruction and provide feedback. This also served to add demonstration data to the data store.
## Technical Challenges
- Frontend processing of data returned in ajax calls to database (MongoDB cursor instances)
- Filtering of entries using MongoDB aggregate function
- Populating data in modals according to clicked element
- Export to csv using DictWriter function
- Attempt on asynchronous execution of notification email to speed up login time
## Deployment
App hosted on Heroku linked to GitHub repository. Environment variables set for sensitive information rather than contained in code. Static CSS and JS files minified for optimal loading speed.

The deployment to Heroku was fairly straightforward, however I did need to specify the Python runtime to match my local machine as well as module requirements and Procfile. The application is linked to the GitHub repository as a deployment and is updated manually to latest commit via Heroku controls.

## Content
All content (incld. background image) produced by myself other than CSS, JS and Google font/icon libraries as documented.

## Acknowledgements
- Bootstrap official documentation
- jQuery official documentation
- Python and Flask official documentation
- HTML5 validator https://validator.w3.org/
- CSS3 validator https://jigsaw.w3.org/css-validator/