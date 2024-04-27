from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, time, timedelta
from bson.objectid import ObjectId
import traceback
from collections import OrderedDict
from calendar import month_abbr

counselor_bp = Blueprint(
    "counselor",
    __name__,
)


client = MongoClient("mongodb://localhost:27017/")
db = client["db_reachOut"]
appointments_collection = db["appointment"]


@counselor_bp.route("/counselor")
def counselor():
    pending_appointments = get_pending_appointments()
    confirmed_appointments = get_confirmed_appointments()
    completed_appointments = list(appointments_collection.find({"status": "completed"}))
    completed_appointments_count = len(completed_appointments)

    if(session.get("counsellor") != True):
        return redirect(url_for('signin'))
    
    return render_template(
        "counsellor.html",
        pending_appointments=pending_appointments,
        confirmed_appointments=confirmed_appointments,
        completed_appointments=completed_appointments,
        completed_appointments_count=completed_appointments_count,
    )


def get_pending_appointments():
    pending_appointments = appointments_collection.find({"status": "pending"})
    return list(pending_appointments)

@counselor_bp.route("/get_available_slots", methods=["POST"])
def get_available_slots():
    # Get the current date
    today = datetime.now().date()

    # Get the start date (tomorrow)
    start_date = today + timedelta(days=1)

    # Adjust the start date to the next Monday if it's a weekend
    while start_date.weekday() > 4:  # Weekday > 4 means it's Saturday or Sunday
        start_date += timedelta(days=1)

    # Get the end date (7 weekdays from the start date)
    end_date = start_date + timedelta(days=6)

    # Initialize an empty list to store available slots for the next 7 weekdays
    available_slots_week = []

    # Loop through the next 7 weekdays
    current_date = start_date
    while current_date <= end_date:
        # Get the list of confirmed appointments for the current day
        confirmed_appointments = appointments_collection.find(
            {
                "status": "confirmed",
                "$or": [
                    {
                        "AppDate": {
                            "$gte": datetime.combine(current_date, time(9, 0)),
                            "$lt": datetime.combine(current_date, time(17, 0)),
                        }
                    },
                    {
                        "AppEndDate": {
                            "$gte": datetime.combine(current_date, time(9, 0)),
                            "$lt": datetime.combine(current_date, time(17, 0)),
                        }
                    },
                ],
            }
        )

        # Generate a list of existing time slots from confirmed appointments
        existing_slots = []
        for appt in confirmed_appointments:
            start_slot = appt["AppDate"]
            end_slot = appt["AppEndDate"]
            for slot_time in [
                start_slot + timedelta(minutes=30 * i)
                for i in range(int((end_slot - start_slot).total_seconds() // 1800))
            ]:
                existing_slots.append(slot_time)

        # Generate a list of available time slots for the current day
        available_slots = []
        start_time = datetime.combine(current_date, time(9, 0))
        end_time = datetime.combine(current_date, time(17, 0))
        current_time = start_time
        while current_time < end_time:
            slot_start = current_time
            slot_end = current_time + timedelta(hours=2)
            if all(
                slot_time not in existing_slots
                for slot_time in [
                    slot_start + timedelta(minutes=30 * i) for i in range(1, 4)
                ]
            ):
                available_slots.append(
                    {
                        "start": f"{slot_start.strftime('%m/%d/%Y %I:%M %p')}",
                        "end": f"{slot_end.strftime('%m/%d/%Y %I:%M %p')}",
                    }
                )
            current_time += timedelta(hours=2)

        # Add the available slots for the current day to the list for the week
        available_slots_week.extend(available_slots)

        # Move to the next weekday
        current_date += timedelta(days=1)

    # Sort the available slots in chronological order
    available_slots_week.sort(
        key=lambda x: datetime.strptime(x["start"], "%m/%d/%Y %I:%M %p")
    )

    return jsonify(available_slots_week)


@counselor_bp.route("/update_appointment", methods=["POST"])
def update_appointment():
    appointment_id = request.form.get("appointment_id")
    slot_start_datetime_str = request.form.get("slot_start_datetime")
    print(slot_start_datetime_str)
    if slot_start_datetime_str is None:
        return jsonify({"error": "Missing slot_start_datetime"}), 400

    try:
        slot_start_datetime = datetime.fromisoformat(slot_start_datetime_str)
        slot_start_datetime += timedelta(hours=5, minutes=30)

        slot_end_datetime = slot_start_datetime + timedelta(hours=2)

        print(
            f"Updating appointment {appointment_id} with start time: {slot_start_datetime} and end time: {slot_end_datetime}"
        )

        # Update the appointment in the database
        result = appointments_collection.update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "AppDate": slot_start_datetime,
                    "AppEndDate": slot_end_datetime,
                    "status": "confirmed",
                }
            },
        )

        print(f"Update result: {result.raw_result}")

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating appointment: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def get_confirmed_appointments():
    confirmed_appointments = appointments_collection.find({"status": "confirmed"})
    return list(confirmed_appointments)


@counselor_bp.route("/save_report", methods=["POST"])
def save_report():
    appointment_id = request.form.get("appointment_id")
    private_notes = request.form.get("private_notes")
    student_notes = request.form.get("student_notes")

    # Check if appointment_id is valid
    if not appointment_id or not ObjectId.is_valid(appointment_id):
        print(f"Invalid appointment_id: {appointment_id}")
        return jsonify({"error": "Invalid appointment ID"}), 400

    try:
        # Update the appointment in the database with the notes
        result = appointments_collection.update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "private_notes": private_notes,
                    "student_notes": student_notes,
                    "status": "completed",
                }
            },
        )

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving report: {e}")
        return jsonify({"error": str(e)}), 500
