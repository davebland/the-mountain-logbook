# The Mountain Logbook

## An online tool for logging a user’s mountain or hill walking experiences. Replicates, and improves on, a traditional paper logbook.

A 'Data Centric Development' milestone project for Code Institute.

The Mountain Logbook Online is a tool for recording details of mountain walking experiences. The essential user requirement is to be able to record and store details of any number of walk/hike/climbs that the user has completed. In essence, a digital logbook with which an individual can keep a record of their experience for personal interest and/or for the purposes of gathering evidence for qualification. There is an export functionality so the complete 'logbook' can be submitted to an awarding body for assessment.

A Python website using the Flask framework with MongoDB datastore.

## Demo
See http://the-mountain-logbook.herokuapp.com/
## UX
The application is primarily for people who will already be keeping a logbook of some kind, likely either a paper based or spreadsheet. For this reason, the user interface will use a table layout as this will be familiar and aid user take-up.
### User Stories
1. On first opening the application the user can either login to an existing account using an email address of create a new account by supplying a unique email address and display name.
2. It will not be possible to create accounts with duplicate email addresses and users will get obvious feedback if an email address already exists.
3. Once logged in it will be obvious how to add a new entry.
4. Existing entries will be clearly displayed and can be filtered by date or mountain area.
5. Existing entries can be amended or deleted by the user.
6. User will see basic statistics for their account including including no. of entries, highest peak and total distance travelled.
7. Entries will be categorized by mountain area and users will be able to add and delete areas without affecting previously created records.
8. There will be a ‘share’ page where users can view selected information from other users’ entries on a per area basis.

## Features
- Basic user authentication by email and subsequent checking of valid session before returning data
- ‘Member since’ derived from timestamp in Mongo ObjectId
- Pagination of entries on home page
- Basic handling of common mongo db errors with custom error page
- Javascript ajax calls to populate ‘details’ modal according to entry selected in table and without reloading page
- Basic email notifications to admin using AWS SES smtp services

## Future Additions
- Directly connect to 'Mountain-Training.org' (UK governing body) website for import into their CMS for candidate assessment.
- More advanced search and filter controls for entries.
- Add pre-dictated highest points (mountain summits) that users can select.
- More advanced interactions with other users including link of entries with other users in the system
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

Tested on different browsers and desktop/mobile screen sizes.

## Technical Challenges
- Asynchronous execution of notification email to speed up login time
## Deployment
App hosted on Heroku linked to GitHub repository. Environment variables set for sensitive information rather than containing this in code. Static css and js minified for optimal loading speed.

## Credits

## Content
All content produced by me other than CSS & JS libraries as documented. Includes background image.

## Acknowledgements
- Bootstrap official documentation
- jQuery official documentation
- Python and Flask official documentation
- HTML5 validator https://validator.w3.org/
- CSS3 validator https://jigsaw.w3.org/css-validator/