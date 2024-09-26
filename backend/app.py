from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import get_video_reccs
from flask import Flask, request, jsonify
from update_courses import *
from pymongo import MongoClient
# Handling Environment Variables
load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify('Welcome to the KnowGap Backend API!')

@app.route('/get_video_rec', methods=['GET'])
def get_video_recc_route():
    reccs = get_video_reccs.get_video_reccomendation()
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


if __name__ == "__main__":
    app.run()