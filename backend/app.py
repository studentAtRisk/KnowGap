from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import get_curated_videos
from flask import Flask, request, jsonify
from flask_cors import CORS
from update_courses import update_db, get_token_collection
from encryption import at_risk_encrypt_token, at_risk_decrypt_token
from pymongo import MongoClient

# Handling Environment Variables
load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
HEX_ENCRYPTION_KEY = os.getenv('HEX_ENCRYPTION_KEY')

encryption_key = bytes.fromhex(HEX_ENCRYPTION_KEY)

from flask import Flask, request, jsonify
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify('Welcome to the KnowGap Backend API!')

@app.route('/get_video_rec', methods=['POST'])
def get_video_recc_route():
    data = request.get_json()
    student_id = data.get('userid')
    course_id = data.get('courseid')
    reccs = get_curated_videos.get_assessment_videos(student_id, course_id)
    return jsonify(reccs)

@app.route('/update_course', methods=['POST'])
def update_course_route():
    data = request.get_json()
    
    courseid = data.get('courseid')
    access_token = data.get('access_token')


    # Make sure there is no missing parameters from request
    if not all([courseid, access_token]):
        return jsonify({'error': 'Missing parameters'}), 400
    update_db(courseid, access_token)

    return jsonify({'status': "Complete"})

# POST endpoint to update or create a user
@app.route('/update-user-auth', methods=['POST'])
def update_course_request_endpoint():
    data = request.get_json()
    userid = data.get('userid')
    access_token = data.get('access_token')
    role = data.get('role')
    courseids = data.get('courseids')

    # validate required parameters
    if not all([userid]):
        return jsonify({'error': 'Missing userid'}), 400
    # More validations:
    if not access_token:
        return jsonify({'error': 'Missing access_token'}), 400
    if not role:
        return jsonify({'error': 'Missing role'}), 400
    # if not courseids:
    #     return jsonify({'error': 'Missing Course Id(s)'}), 400

    token_collection = get_token_collection()
    encrypted_token = at_risk_encrypt_token(encryption_key, access_token)

    if role == "student":
        try:
            token_collection.update_one({'_id': userid},{"$set": {"auth": encrypted_token, "role": role}},upsert=True)
        except Exception as e:
            return jsonify({
                'error': f'problem in db: {e}'
            })
    else:
        token_collection.update_one({'_id': userid},{"$set": {"auth": encrypted_token, "role": role, "courseids": courseids}},upsert=True)

    # return updated user details
    updated_user = token_collection.find_one({'_id': userid}, {'_id': 0})  # Exclude _id in the result
    if updated_user:
        return jsonify({'status': 'Complete', 'user_details': updated_user['role']}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404
    
# GET endpoint to retrieve user data
@app.route('/get-user', methods=['GET'])
def get_user():
    # get the userid from query parameters (e.g., /get_user?userid=123)

    data = request.get_json()
    userid = data.get('userid')

    if not userid:
        return jsonify({'error': 'Missing userid parameter'}), 400
    
    token_collection = get_token_collection()

    # fetch the user from MongoDB
    user = token_collection.find_one({'_id': userid})  # Exclude _id in the result

    if user:
        # return jsonify({'status': 'Success', 'user_details': user})
        decrypted_token = at_risk_decrypt_token(encryption_key, user['auth'])
        return jsonify({
            'status' : 'Success',
            "user_details": {
                "_id": user["_id"],
                "auth": decrypted_token,
                "role": user["role"]
            }
        }), 200
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404

if __name__ == "__main__":
    app.run()
