from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandomstring")

""" Route handler functions """

def login_check():
    # If user logged in return true otherwise false
    if 'user_id' in session:
        return True
    return False

""" Routes """

@app.route('/')
def index():
    if login_check():
        return render_template('logbook-home.html', title="Logbook Home")
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
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
    # Destroy session and return to home
    session.clear()
    return redirect(url_for('index'))

@app.route('/new')
def new():
    """ Generate page for new entry """
    if login_check():
        return render_template('update.html', title="New Entry")
    return redirect( url_for('index') )

@app.route('/update/<entry_id>')
def update(entry_id):
    """ Generate page to update existing entry """
    if login_check():
        return render_template('update.html', title="Edit Entry")
    return redirect( url_for('index') )

@app.route('/get/<entry_id>')
def get(entry_id):
    """ Return all fields of record """
    return "{'test' : %s }" % entry_id

# Set flask parameters
if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True)