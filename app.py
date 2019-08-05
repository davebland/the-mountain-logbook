from flask import Flask, render_template

app = Flask(__name__)



@app.route('/')
def home():
    return render_template('login.html')

@app.route('/home')
def temp():
    return render_template('logbook-home.html')

@app.route('/add_edit')
def add_edit_entry():
    return render_template('add-edit-entry.html')
    
# Set flask parameters
if __name__ == '__main__':
    app.run(debug=True)