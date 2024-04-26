# appointment.py (Flask Blueprint)
from flask import Blueprint, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

appointment_bp = Blueprint("appointment", __name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["db_reachOut"]
appointments_collection = db["appointment"]


@appointment_bp.route("/bookAppointment", methods=["POST"])
def bookAppointment():
    user_id = session.get("uid")
    reason = request.form.get("reason")

    name = session.get("name")
    email = session.get("email")

    appointment_data = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "reason": reason,
        "AppDate": None,
        "status": "pending",
    }

    # Insert the appointment data into the MongoDB collection
    result = appointments_collection.insert_one(appointment_data)

    session["successAppoin"] = True
    return redirect(url_for("user"))


@appointment_bp.route("/cancelAppointment", methods=["POST"])
def cancelAppointment():
    appointment_id = request.form.get("appointment_id")
    if appointment_id:
        # Delete the appointment from the MongoDB collection
        appointments_collection.delete_one({"_id": ObjectId(appointment_id)})
    return redirect(url_for("user"))
