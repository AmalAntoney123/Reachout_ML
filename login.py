from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import bcrypt

login_bp = Blueprint('login', __name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['db_reachOut']
collection = db['user']


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email exists in the database
        user = collection.find_one({'email': email})
        if user:
            # Check if the user is enabled
            if user['is_enabled']:
                # Check if the password matches the hashed password in the database
                if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    # Set session variables for user authentication
                    session['email'] = email
                    session['name'] = user['name']
                    session['age'] = user['age']
                    session['gender'] = user['gender']
                    session['uid'] = str(user['_id'])
                    if (session.get('name') == "counselor"):
                        session['counsellor'] = True
                        return redirect(url_for('counselor.counselor'))
                    if (session.get('name') == "admin"):
                        session['admin'] = True
                        return redirect(url_for('admin.admin'))
                    # Redirect to the home page after login
                    return redirect(url_for('user'))
                else:
                    # Incorrect password
                    session['error'] = 'Invalid email or password'
                    return redirect(url_for('signin'))
            else:
                # User is disabled
                flash('Your account has been disabled. Please contact an administrator.', 'danger')
                return redirect(url_for('signin'))
        else:
            # User with the given email does not exist
            session['error'] = 'User does not exist'
            return redirect(url_for('signin'))