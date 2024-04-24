from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import datetime
from pymongo import MongoClient

journal_bp = Blueprint('journal', __name__, template_folder='templates')

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['db_reachOut']
collection = db['journal']

@journal_bp.route('/newJournal', methods=['GET', 'POST'])
def newJournal():
    if request.method == 'POST':
        entry_text = request.form['entry']
        current_date = datetime.date.today().strftime('%B %d, %Y')
        
        userID = session.get('uid')
        query = {'userID': userID, 'date': current_date}
        todayJournal = list(collection.find(query))

        if entry_text.strip():
            
            entry = {
                'date': current_date,
                'text': entry_text,
                'userID': session.get('uid')
            }
            
            if todayJournal:
                # Update the existing document
                collection.update_one(query, {'$set': {'text': entry_text}})
            else:
                # Insert a new document
                collection.insert_one(entry)
                
            session['success'] = True
            return redirect(url_for('user'))
        else:
            flash('Please enter your journal entry', 'error')

    journal_entries = list(collection.find({}, {'_id': False}))
    return render_template('user.html', journal_entries=journal_entries, show_modal=False)
