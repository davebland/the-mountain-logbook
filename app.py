from flask import Flask, render_template, request
import os

app = Flask(__name__)

""" Route handler functions """



""" Routes """

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return request.form
    return render_template('login.html')

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