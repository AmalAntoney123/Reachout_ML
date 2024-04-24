from flask import Flask, render_template,session, redirect, url_for, request
from pymongo import MongoClient
import datetime 
import math
import random

from register import register_bp
from login import login_bp
from journal import journal_bp
from quotes import quotes 


app = Flask(__name__)

app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(journal_bp)

app.secret_key = 'secret_key123'

client = MongoClient('mongodb://localhost:27017/')
db = client['db_reachOut']
collection = db['journal']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    message = session.pop('message', None)
    error = session.pop('error', None)
    # Render the signin template with the success message
    return render_template('signin.html', message=message,error=error)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/template')
def template():
    return render_template('template.html')

@app.route('/user')
def user():
    userName = session.get('name')
    userEmail = session.get('email')
    userAge = session.get('age')
    userID = session.get('uid')
    userGender = session.get('gender')
    success = session.pop('success', None)
    current_date = datetime.date.today().strftime('%B %d, %Y')
    query = {'userID': userID, 'date': current_date}
    todayJournal = list(collection.find(query))

    if not userName or not userEmail or not userAge:
        return redirect(url_for('signin'))

    quote = get_quote_for_day()

    return render_template('user.html', userEmail=userEmail, userName=userName, userAge=userAge,
                           userID=userID, success=success, todayJournal=todayJournal,
                           userGender=userGender, quote=quote['quote'], author=quote['author'])
    
def get_quote_for_day():
    today = datetime.date.today().isoformat()
    if 'quote_date' not in session or session['quote_date'] != today:
        random_quote = random.choice(quotes)
        session['quote'] = random_quote
        session['quote_date'] = today
    return session['quote']

@app.route('/get_entries', methods=['GET'])
def get_entries():
    userID = session.get('uid')
    page = request.args.get('page', 1, type=int)
    page_size = 5  # Number of entries per page

    total_entries = collection.count_documents({'userID': userID})
    skip_count = (page - 1) * page_size
    entries = list(collection.find({'userID': userID}).skip(skip_count).limit(page_size))

    # Render the entries as HTML
    entries_html = render_template('_entries.html', entries=entries)

    return ({
        'entries_html': entries_html,
        'total_pages': math.ceil(total_entries / page_size)
    })
    
@app.route('/logout')
def logout():
    # Clear session data
    session.pop('name', None)
    session.pop('email', None)
    session.pop('gender', None)
    session.pop('uid', None)
    session.pop('age', None)
    # Redirect to the sign-in page
    return redirect(url_for('signin'))  # Assuming your sign-in route is named 'signin'


if __name__ == '__main__':
    app.run(debug=True)