from flask import render_template, request, redirect, session, url_for
from app import app, mysql
from datetime import datetime

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']
        blood_group = request.form['blood_group']
        location = request.form['location']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, phone, password, role, blood_group, location) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
            (name, email, phone, password, role, blood_group, location))
        mysql.connection.commit()
        cur.close()
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s AND role=%s", (email, password, role))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['role'] = user[5]
            session['blood_group'] = user[6]
            session['location'] = user[7]

            if role == 'donor':
                return redirect('/donor_dashboard')
            elif role == 'recipient':
                return redirect('/recipient_dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Donor Dashboard
@app.route('/donor_dashboard')
def donor_dashboard():
    if 'user_id' not in session or session['role'] != 'donor':
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM blood_requests WHERE location = %s AND blood_group_needed = %s ORDER BY urgency DESC", 
        (session['location'], session['blood_group']))
    requests = cur.fetchall()
    cur.close()

    return render_template('donor_dashboard.html',
        donor_name=session['name'],
        blood_group=session['blood_group'],
        location=session['location'],
        availability=True,  # Hardcoded for now
        requests=[{
            'blood_group': r[2],
            'location': r[3],
            'urgency': r[4],
            'contact': r[6]
        } for r in requests]
    )

# Recipient Dashboard
@app.route('/recipient_dashboard')
def recipient_dashboard():
    if 'user_id' not in session or session['role'] != 'recipient':
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE location = %s AND blood_group = %s AND role = 'donor' AND availability = TRUE", 
        (session['location'], session['blood_group']))
    donors = cur.fetchall()
    cur.close()

    return render_template('recipient_dashboard.html',
        recipient_name=session['name'],
        matching_donors=[{
            'name': d[1],
            'blood_group': d[6],
            'phone': d[3]
        } for d in donors]
    )

# Handle Blood Request
@app.route('/request_blood', methods=['POST'])
def request_blood():
    if 'user_id' not in session or session['role'] != 'recipient':
        return redirect('/login')

    blood_group_needed = request.form['blood_group_needed']
    location = request.form['location']
    hospital_name = request.form['hospital_name']
    contact = request.form['contact']
    urgency = request.form['urgency']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO blood_requests (user_id, blood_group_needed, location, urgency, hospital_name, contact, request_time) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
        (session['user_id'], blood_group_needed, location, urgency, hospital_name, contact, datetime.now()))
    mysql.connection.commit()
    cur.close()

    return redirect('/recipient_dashboard')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
