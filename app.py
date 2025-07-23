from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sriram#2010'  # replace with your password
app.config['MYSQL_DB'] = 'blood_donation'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

# Add routes for register, login, dashboard, etc.

if __name__ == '__main__':
    app.run(debug=True)
