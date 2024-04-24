from flask import request, redirect, url_for, Blueprint, session
from pymongo import MongoClient
import bcrypt

register_bp = Blueprint('register', __name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['db_reachOut']
collection = db['user']

@register_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        plaintext_password = request.form['password']  # Get plaintext password

        # Encrypt the password using bcrypt
        hashed_password = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
        year_of_study = request.form['year_of_study']

        # Insert data into MongoDB
        user_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'email': email,
            'password': hashed_password,
            'year_of_study': year_of_study
        }
        collection.insert_one(user_data)

        # Set a session variable to store the success message
        session['message'] = 'Successfully registered'

        # Redirect to a success page or back to the sign-up page
        return redirect(url_for('signin'))


