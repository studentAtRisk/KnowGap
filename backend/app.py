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
from update_course_students import update_db as update_students_db
from update_course_quizzes import update_db as update_quizzes_db
import asyncio

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

@app.route('/get-video-rec', methods=['POST'])
def get_video_recc_route():
    data = request.get_json()  # Extract JSON payload
    print(f"Received data: {data}")  # Log incoming request data for debugging
    
    student_id = data.get('userid')
    course_id = data.get('courseid')
    
    # Input validation with logging
    if not student_id:
        print("Missing Student ID")
        return jsonify({'error': 'Missing Student ID'}), 400
    if not course_id:
        print("Missing Course ID")
        return jsonify({'error': 'Missing Course ID'}), 400
    
    # Call the logic that works locally
    reccs = get_curated_videos.get_assessment_videos(student_id, course_id)
    print(f"Returning recommendations: {reccs}")  # Log the returned data
    return jsonify(reccs)
#@app.route('/get-video-rec', methods=['POST'])
# def get_video_recc_route():
#     data = request.get_json()
#     student_id = data.get('userid')
#     course_id = data.get('courseid')
    
#     # Input Validations
#     if not student_id:
#         return jsonify({'error': 'Missing Student ID'})
#     if not course_id:
#         return jsonify({'error': 'Missing Course ID'})
    
#     reccs = get_curated_videos.get_assessment_videos(student_id, course_id)
#     return jsonify(reccs)

@app.route('/update-course', methods=['POST'])
def update_course_route():
    data = request.get_json()
    
    course_id = data.get('courseid')
    access_token = data.get('access_token')
    
    # Input Validations
    if not course_id:
        return jsonify({'error': 'Missing Course ID'}), 400
    if not access_token:
        return jsonify({'error': 'Missing Access Token'}), 400
    
    update_db(course_id, access_token)

    return jsonify({'status': "Complete"})

# POST endpoint to update or create a user
@app.route('/update-user-auth', methods=['POST'])
def update_course_request_endpoint():
    data = request.get_json()
    user_id = data.get('userid')
    access_token = data.get('access_token')
    course_ids = data.get('courseids')

    # Input Validations
    if not user_id:
        return jsonify({'error': 'Missing User ID'}), 400
    if not access_token:
        return jsonify({'error': 'Missing Access Token'}), 400
    if not all([course_ids]):
        return jsonify({'error': 'Missing Course ID(s)'}), 400

    token_collection = get_token_collection()
    encrypted_token = at_risk_encrypt_token(encryption_key, access_token)

    token_collection.update_one({'_id': user_id},{"$set": {"auth": encrypted_token, "courseids": course_ids}},upsert=True)

    # return updated user details
    updated_user = token_collection.find_one({'_id': user_id}, {'_id': 0})
    if updated_user:
        return jsonify({'status': 'Complete'}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404
    
# GET endpoint to retrieve user data
@app.route('/get-user', methods=['GET'])
def get_user():
    data = request.get_json()
    userid = data.get('userid')

    if not userid:
        return jsonify({'error': 'Missing user ID(s) parameter'}), 400
    
    token_collection = get_token_collection()

    # fetch the user from MongoDB
    user = token_collection.find_one({'_id': userid})

    if user:
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

@app.route('/update_course_request', methods=['POST'])
async def update_course_request_endpoint():
    data = request.get_json()
    
    courseid = int(data.get('courseid'))
    access_token = data.get('access_token')
    authkey = data.get('authkey')
    link = data.get('link')


    # Make sure there is no missing parameters from request
    if not all([courseid, access_token, authkey]):
        return jsonify({'error': 'Missing parameters'}), 400
    await update_students_db(courseid, access_token, authkey, link)
    await update_quizzes_db(courseid, access_token, authkey, link)

    return jsonify({'status': "Complete"})
