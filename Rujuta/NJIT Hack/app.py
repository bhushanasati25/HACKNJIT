from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Points for completing tasks
POINTS_FULL = 10
POINTS_PARTIAL = 5

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup form submission (e.g., saving user info to the database)
        return redirect(url_for('login'))
    return render_template('signup.html')


# Dashboard Page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Patient Compliance Page
@app.route('/patient/<int:patient_id>')
def patient_page(patient_id):
    # Fetch patient details, points, and prescriptions
    patient = {'name': 'John Doe', 'points': 150}
    prescriptions = {
        'medicines': [{'id': 1, 'name': 'Aspirin'}, {'id': 2, 'name': 'Vitamin C'}],
        'exercises': [{'id': 3, 'name': 'Walking', 'goal': '2 miles'}],
        'diets': [{'id': 4, 'name': 'Low-carb'}]
    }
    greeting = "Good Morning" if datetime.now().hour < 12 else "Good Afternoon"
    return render_template('patient_page.html', patient_name=patient['name'], 
                           patient_points=patient['points'], greeting=greeting,
                           medicines=prescriptions['medicines'],
                           exercises=prescriptions['exercises'], diets=prescriptions['diets'])

# Doctor’s Prescription Page
@app.route('/doctor/<int:patient_id>/prescribe', methods=['GET', 'POST'])
def prescribe(patient_id):
    if request.method == 'POST':
        # Save prescription data (medicines, diet, exercise)
        return redirect(url_for('dashboard'))
    return render_template('prescription.html', patient_id=patient_id)

# Endpoint to mark completion and award points
@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    data = request.json
    item_id = data['item_id']
    status = data['status']
    
    # Calculate points based on completion status
    points_earned = POINTS_FULL if status == 'complete' else POINTS_PARTIAL if status == 'partial' else 0
    # Update points in the database (logic not shown)
    return jsonify({'success': True, 'points_earned': points_earned})

######################################################################################################

import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/your/firebase_key.json')  # Replace with your actual key file path
firebase_admin.initialize_app(cred)
db = firestore.client()  # Initialize Firestore


if __name__ == '__main__':
    app.run(debug=True)
