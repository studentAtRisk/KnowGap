from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import get_curated_videos
from flask import Flask, request, jsonify
from update_courses import updatedb, get_token_collection
from encryption import encrypt_token_real, decrypt_token
from pymongo import MongoClient

# Handling Environment Variables
load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
HEX_ENCRYPTION_KEY = os.getenv('HEX_ENCRYPTION_KEY')

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify('Welcome to the KnowGap Backend API!')

@app.route('/get_video_rec', methods=['GET'])
def get_video_recc_route():
    data = request.get_json()
    student_id = data.get('userid')
    course_id = data.get('courseid')
    reccs = get_curated_videos.get_video_recommendation(student_id, course_id)
    return jsonify(reccs)

@app.route('/update_course', methods=['POST'])
def update_course_route():
    data = request.get_json()
    
    courseid = data.get('courseid')
    access_token = data.get('access_token')


    # Make sure there is no missing parameters from request
    if not all([courseid, access_token]):
        return jsonify({'error': 'Missing parameters'}), 400
    updatedb(courseid, access_token)

    return jsonify({'status': "Complete"})

@app.route('/encrypttoken', methods=['POST'])
def encrypt_token():
    payload = request.get_json()
    
    if not payload:
        return jsonify({'error': 'Missing parameters'}), 400
    
    token_to_be_encrypted = payload.get('token')
    user_id = payload.get('userId')
    
    if not all([user_id, token_to_be_encrypted]):
        return jsonify({'error': 'Missing parameters'})
    
    # Getting the token collection for saving:
    db_token_collection = get_token_collection()
    
    # Switching key from hex to bytes
    encryption_key = bytes.fromhex(HEX_ENCRYPTION_KEY)
    
    encrypted_token = encrypt_token_real(encryption_key, token_to_be_encrypted)
    
    try:
        # db_token_collection.update_one({'_id': user_id, 'token': encrypted_token})
        db_token_collection.update_one({'_id': user_id}, {'$set': {'token': encrypted_token}})
    except Exception as e:
        return jsonify({'message': f'error with db saving: {e}'})
    
    
    return jsonify({'message': 'success'}), 200

if __name__ == "__main__":
    app.run()