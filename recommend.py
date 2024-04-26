from flask import Blueprint, request, jsonify, session, redirect, url_for
from datetime import timedelta, datetime
import datetime
from model import model
import traceback
from pymongo import MongoClient

recommend_bp = Blueprint("recommend", __name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["db_reachOut"]
collection = db["journal"]
appointments_collection = db["appointment"]
mood_collection = db["mood"]


@recommend_bp.route("/recommendation", methods=["POST"])
def recommendation():
    try:
        form_data = request.get_json()
        userAge = session.get("age")
        userGender = 1 if session.get("gender") == "male" else 2

        # Extract the feature values from the form data
        Q1_Stress = form_data.get("stress")
        Q2_Anxiety = form_data.get("anxiety")
        Q3_Depression = form_data.get("depression")
        Q4_Sleep = form_data.get("sleep")
        Q5_Social = form_data.get("social")

        # Store the form data values in the session

        # Create a feature vector
        feature_vector = [
            [
                userAge,
                userGender,
                Q1_Stress,
                Q2_Anxiety,
                Q3_Depression,
                Q4_Sleep,
                Q5_Social,
            ]
        ]

        # Make a prediction using the trained model
        prediction = model.predict(feature_vector)[0]

        if prediction == "Counseling":
            recommendation = "You should seek counseling for your well-being."
        elif prediction == "Exercise":
            recommendation = (
                "You should incorporate regular exercise into your routine."
            )
        elif prediction == "Therapy":
            recommendation = "You should explore therapy as a potential solution."
        elif prediction == "Mindfulness":
            recommendation = "You should practice mindfulness techniques to improve your mental state."
        elif prediction == "Support Group":
            recommendation = "You should join a support group to connect with others in similar situations."
        elif prediction == "Stress Management":
            recommendation = (
                "You should implement effective stress management strategies."
            )
        elif prediction == "Physical Activity":
            recommendation = "You should engage in physical activities to boost your overall well-being."
        elif prediction == "Psychotherapy":
            recommendation = "You should seek psychotherapy to address your concerns."
        elif prediction == "Yoga":
            recommendation = "You should incorporate yoga into your routine for mental and physical benefits."
        elif prediction == "Social Support":
            recommendation = (
                "You should seek social support from your loved ones or community."
            )
        elif prediction == "Meditation":
            recommendation = "You should practice meditation to cultivate mindfulness and inner peace."
        elif prediction == "Life Coach":
            recommendation = (
                "You should work with a life coach to help you achieve your goals."
            )
        elif prediction == "Group Therapy":
            recommendation = "You should explore group therapy as a potential solution."
        elif prediction == "Time Management":
            recommendation = (
                "You should implement effective time management strategies."
            )
        elif prediction == "CBT (Cognitive Behavioral Therapy)":
            recommendation = "You should try Cognitive Behavioral Therapy (CBT) to address your concerns."
        elif prediction == "Self-Care":
            recommendation = (
                "You should prioritize self-care practices for your overall well-being."
            )
        else:
            recommendation = "The recommendation is not recognized."

        user_id = session.get("uid")
        mood_data = {
            "user_id": user_id,
            "stress": Q1_Stress,
            "anxiety": Q2_Anxiety,
            "depression": Q3_Depression,
            "sleep": Q4_Sleep,
            "social": Q5_Social,
            "recommendation": recommendation,
            "mood_date": datetime.date.today().isoformat(),
        }
        mood_collection.insert_one(mood_data)

        # Redirect to the /user route
        return redirect(url_for("user"))

    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500