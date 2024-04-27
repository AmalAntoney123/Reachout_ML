from flask import Blueprint, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


admin_bp = Blueprint("admin", __name__, template_folder="templates")

client = MongoClient("mongodb://localhost:27017/")
db = client["db_reachOut"]
users_collection = db["user"]
feedback_collection = db["feedback"]


@admin_bp.route("/admin")
def admin():
    users = list(users_collection.find({"name": {"$nin": ["admin", "counselor"]}}))
    feedbacks = list(feedback_collection.find())
    return render_template("admin.html", users=users, feedbacks=feedbacks)

@admin_bp.route('/update_user_status', methods=['POST'])
def update_user_status():
    user_id = request.form.get('user_id')
    is_enabled = request.form.get('is_enabled') == 'false'
    print(user_id)
    # Update the user's status in the database
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'is_enabled': is_enabled}}
    )

    return jsonify({'message': 'User status updated successfully'})
