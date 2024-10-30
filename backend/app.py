from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import get_curated_videos
from quart import Quart, request, jsonify
from quart_cors import cors
from update_courses import update_db, get_token_collection
from encryption import at_risk_encrypt_token, at_risk_decrypt_token
from pymongo import MongoClient
from update_course_students import update_db as update_students_db
from update_course_quizzes import update_db as update_quizzes_db
from update_course_context import update_context
from update_video import update_video_link
from get_video_reccs import update_course_videos, update_videos_for_filter
import logging
import asyncio
from get_support_video import get_videos_for_risk_level, get_random_video

# Handling Environment Variables
load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
HEX_ENCRYPTION_KEY = os.getenv('HEX_ENCRYPTION_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

encryption_key = bytes.fromhex(HEX_ENCRYPTION_KEY)

app = Quart(__name__)
cors(app)

client = MongoClient(DB_CONNECTION_STRING)
db = client["KnowGap"]
tokens_collection = db["Tokens"]
quizzes_collection = db['Quiz Questions']

@app.route('/')
async def hello_world():
    return jsonify('Welcome to the KnowGap Backend API!')

@app.route('/update-all-videos', methods=['POST'])
async def update_all_videos():
    videos = update_videos_for_filter()
    return jsonify(videos)

@app.route('/update-course-videos', methods=['POST'])
async def update_course_videos_route():
    data = await request.get_json()
    course_id = data.get('courseid')

    if not course_id:
        print("Missing Course ID")
        return jsonify({'error': 'Missing Course ID'}), 400
    return await update_course_videos(course_id)

@app.route('/get_course_videos', methods=['GET'])
async def get_videos_for_course():
    course_id = request.args.get('course_id')

    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400
    
    # Call the get_course_videos function
    result = await get_curated_videos.get_course_videos(course_id=course_id)
    
    # Return the result as a JSON response
    return jsonify(result)

@app.route('/get-video-rec', methods=['POST'])
async def get_video_recc_route():
    data = await request.get_json()  # Extract JSON payload
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
    reccs = await get_curated_videos.get_assessment_videos(student_id, course_id)
    print(f"Returning recommendations: {reccs}")  # Log the returned data
    return jsonify(reccs)

@app.route('/update-course', methods=['POST'])
async def update_course_route():
    data = await request.get_json()
    
    course_id = data.get('courseid')
    access_token = data.get('access_token')
    
    # Input Validations
    if not course_id:
        return jsonify({'error': 'Missing Course ID'}), 400
    if not access_token:
        return jsonify({'error': 'Missing Access Token'}), 400
    
    await update_db(course_id, access_token)

    return jsonify({'status': "Complete"})

# POST endpoint to update or create a user
@app.route('/add-token', methods=['POST'])
async def add_user_token():
    data = await request.get_json()
    user_id = data.get('userid')
    access_token = data.get('access_token')
    course_ids = data.get('courseids')
    link = data.get('link')

    # Input Validations
    if not user_id:
        return jsonify({'error': 'Missing User ID'}), 400
    if not access_token:
        return jsonify({'error': 'Missing Access Token'}), 400
    if course_ids is None:
        return jsonify({'error': 'Missing Course ID(s)'}), 400
    if not link:
        return jsonify({'error': 'Missing Base Link'}), 400

    token_collection = get_token_collection()
    encrypted_token = at_risk_encrypt_token(encryption_key, access_token)

    token_collection.update_one({'_id': user_id}, {"$set": {"auth": encrypted_token, "courseids": course_ids, "link": link}}, upsert=True)

    # return updated user details
    updated_user = token_collection.find_one({'_id': user_id}, {'_id': 0})
    if updated_user:
        return jsonify({'status': 'Complete'}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404
    
# GET endpoint to retrieve user data
@app.route('/get-user', methods=['GET'])
async def get_user():
    data = await request.get_json()
    userid = data.get('userid')

    if not userid:
        return jsonify({'error': 'Missing user ID(s) parameter'}), 400
    
    token_collection = get_token_collection()

    # fetch the user from MongoDB
    user = token_collection.find_one({'_id': userid})

    if user:
        decrypted_token = at_risk_decrypt_token(encryption_key, user['auth'])
        return jsonify({
            'status': 'Success',
            "user_details": {
                "_id": user["_id"],
                "auth": decrypted_token,
                "courseids": user["courseids"],
                "link": user["link"]
            }
        }), 200
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404

# POST endpoint to update course requests asynchronously
@app.route('/update_course_request', methods=['POST'])
async def update_course_request_endpoint():
    data = await request.get_json()
    
    courseid = int(data.get('courseid'))
    access_token = data.get('access_token')
    authkey = data.get('authkey')
    link = data.get('link', '').replace("https://", "").replace("http://", "")

    # Make sure there are no missing parameters from request
    if not all([courseid, access_token, authkey]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        await update_students_db(courseid, access_token, authkey, link)
    except Exception as e:
        return jsonify({'error': f'Error updating students collection: {str(e)}'}), 500
    
    try:
        await update_quizzes_db(courseid, access_token, authkey, link)
    except Exception as e:
        return jsonify({'error': f'Error updating quizzes collection: {str(e)}'}), 500
    
    return jsonify({'status': "Complete"})

@app.route('/update_video', methods=['POST'])
async def update_video():
    data = await request.get_json()
    quizid = data.get('quizid')
    questionid = data.get('questionid')
    old_link = data.get('old_link')
    new_link = data.get('new_link')

    if not all([quizid, old_link, new_link, questionid]):
        return jsonify({'error': 'Missing parameters'}), 400

    update_result = await update_video_link(quizid, questionid, old_link, new_link)
    
    if 'error' in update_result:
        return jsonify({'error': update_result['error']}), 400
    
    return jsonify({'message': update_result['message']}), 200

@app.route('/update_course_context', methods=['POST'])
async def update_course_context_request():
    data = await request.get_json()
    courseid = data.get('courseid')
    new_course_context = data.get('course_context')

    if not all([courseid, new_course_context]):
         return jsonify({'error': 'Missing parameters'}), 400
    update_result = await update_context(courseid, new_course_context)

    if 'error' in update_result:
        return jsonify({'error': update_result['error']}), 400
    
    return jsonify({'message': update_result['message']}), 200

@app.route('/get-questions-by-course/<course_id>', methods=['GET'])
async def get_questions_by_course(course_id):
    results = quizzes_collection.find({"courseid": course_id})

    all_questions = []
    
    for result in results:
        result["_id"] = str(result["_id"])
        all_questions.append(result)

    if not all_questions:
        return jsonify({"message": "No questions found for the given course ID"}), 404

    return jsonify({"course_id": course_id, "questions": all_questions}), 200

@app.route('/get-support-video', methods=['GET'])
async def get_support_video():
    data = await request.get_json()
    risk_level = data.get('risk')

    if not risk_level or risk_level not in ["low", "medium", "high"]:
        return jsonify("Invalid risk submitted!")
    
    result_videos =  await get_videos_for_risk_level(risk_level)
    random_video =  get_random_video(result_videos)
    return jsonify(random_video)

@app.route('/add-video', methods=['POST'])
def add_video():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    

@app.route('remove-video')
def remove_video():
    data = request.get_json()

if __name__ == "__main__":
    app.run(debug=True)
