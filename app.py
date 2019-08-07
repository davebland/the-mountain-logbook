from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET", "arandomstring")

""" Route handler functions """

""" Routes """

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return redirect(url_for('login'), code=307)    
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    if 'login-email' in request.form:
        # Set email as user_id in session
        session["user_id"] = request.form['login-email']
        return "SESSION USER ID:" + session["user_id"]
    return request.form

@app.route('/home')
def temp():
    return render_template('logbook-home.html')

@app.route('/add_edit')
def add_edit_entry():
    return render_template('add-edit-entry.html')

# Set flask parameters
if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True)