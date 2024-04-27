from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from pymongo import MongoClient
from datetime import timedelta, datetime
import datetime
import math
import random
from bson.objectid import ObjectId

from register import register_bp
from login import login_bp
from journal import journal_bp
from quotes import quotes
from recommend import recommend_bp
from appointment import appointment_bp
from chat import chat_bp
from counselor import counselor_bp
from admin import admin_bp

app = Flask(__name__)

app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(journal_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(counselor_bp)
app.register_blueprint(admin_bp)

app.secret_key = "secret_key123"

client = MongoClient("mongodb://localhost:27017/")
db = client["db_reachOut"]
collection = db["journal"]
appointments_collection = db["appointment"]
mood_collection = db["mood"]
users_collection = db["users"]
feedback_collection = db["feedback"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signin")
def signin():
    message = session.pop("message", None)
    error = session.pop("error", None)
    # Render the signin template with the success message
    return render_template("signin.html", message=message, error=error)


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/template")
def template():
    return render_template("template.html")


@app.route("/user")
def user():
    userName = session.get("name")
    userEmail = session.get("email")
    userAge = session.get("age")
    userID = session.get("uid")
    userGender = session.get("gender")

    user_id = session.get("uid")


    mood_data = mood_collection.find_one({"user_id": user_id})
    
    mood = []
    if mood_data:
        if mood_data.get("stress"):
            mood.append({"name": "stress", "value": mood_data["stress"]})
        if mood_data.get("anxiety"):
            mood.append({"name": "anxiety", "value": mood_data["anxiety"]})
        if mood_data.get("depression"):
            mood.append({"name": "depression", "value": mood_data["depression"]})
        if mood_data.get("sleep"):
            mood.append({"name": "sleep", "value": mood_data["sleep"]})
        if mood_data.get("social"):
            mood.append({"name": "social", "value": mood_data["social"]})
        if mood_data.get("recommendation"):
            mood.append({"name": "recommendation", "value": mood_data["recommendation"]})
    
    if(mood_data):
        today = datetime.date.today().isoformat()
        if mood_data["mood_date"] != today:
            mood = []
            mood_collection.delete_one({"user_id": user_id})


    success = session.pop("success", None)
    successAppoin = session.pop("successAppoin", None)
    user_id = session.get("uid")
    appointment = appointments_collection.find_one(
        {"user_id": user_id, "status": {"$ne": "completed"}}
    )
    completed_appointments = appointments_collection.find(
        {"user_id": user_id, "status": "completed"}
    )

    current_date = datetime.date.today().strftime("%B %d, %Y")
    query = {"userID": userID, "date": current_date}
    todayJournal = list(collection.find(query))

    if not userName or not userEmail or not userAge:
        return redirect(url_for("signin"))

    quote = get_quote_for_day()

    has_feedback = feedback_collection.count_documents({"user_id": user_id}) > 0

    return render_template(
        "user.html",
        userEmail=userEmail,
        userName=userName,
        userAge=userAge,
        userID=userID,
        success=success,
        todayJournal=todayJournal,
        userGender=userGender,
        quote=quote["quote"],
        author=quote["author"],
        mood=mood,
        successAppoin=successAppoin,
        appointment=appointment,
        completed_appointments=completed_appointments,
        has_feedback=has_feedback,
    )


def get_quote_for_day():
    today = datetime.date.today().isoformat()
    if "quote_date" not in session or session["quote_date"] != today:
        random_quote = random.choice(quotes)
        session["quote"] = random_quote
        session["quote_date"] = today
    return session["quote"]


@app.route("/get_entries", methods=["GET"])
def get_entries():
    userID = session.get("uid")
    page = request.args.get("page", 1, type=int)
    page_size = 5  # Number of entries per page

    total_entries = collection.count_documents({"userID": userID})
    skip_count = (page - 1) * page_size
    entries = list(
        collection.find({"userID": userID}).skip(skip_count).limit(page_size)
    )

    # Render the entries as HTML
    entries_html = render_template("_entries.html", entries=entries)

    return {
        "entries_html": entries_html,
        "total_pages": math.ceil(total_entries / page_size),
    }


@app.route("/logout")
def logout():
    # Clear session data
    session.pop("name", None)
    session.pop("email", None)
    session.pop("gender", None)
    session.pop("uid", None)
    session.pop("age", None)
    session.pop("counsellor", None)
    session.pop("admin", None)
    # Redirect to the sign-in page
    return redirect(url_for("signin"))  # Assuming your sign-in route is named 'signin'


@app.route("/moodRecommendation")
def moodRecommendation():
    userName = session.get("name")
    return render_template("recommend.html", userName=userName)

@app.route("/moodReset")
def moodReset():
    user_id = session.get("uid")
    mood = []
    mood_collection.delete_one({"user_id": user_id})
    return redirect(url_for("user"))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    feedback_data = request.get_json()
    rating = feedback_data.get('rating')
    feedback_text = feedback_data.get('feedback')
    user_id = session.get('uid')  # Assuming you have a session variable storing the user ID
    print(rating,",",feedback_text,",",user_id)
    if rating and feedback_text and user_id:
        feedback_doc = {
            'user_id': user_id,
            'rating': rating,
            'feedback': feedback_text,
        }
        feedback_collection.insert_one(feedback_doc)
        return jsonify({'message': 'Feedback submitted successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid feedback data.'}), 400
    
if __name__ == "__main__":
    app.run(debug=True)
