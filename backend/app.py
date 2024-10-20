import logging
import asyncio
from quart import Quart, request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from encryption import at_risk_encrypt_token, at_risk_decrypt_token
from update_course_students import update_db as update_students_db
from update_course_quizzes import update_db as update_quizzes_db
from update_course_context import update_context
from update_video import update_video_link
import get_curated_videos  # Ensure this is properly imported for the video recommendations logic

# Handling Environment Variables
load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
HEX_ENCRYPTION_KEY = os.getenv('HEX_ENCRYPTION_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

encryption_key = bytes.fromhex(HEX_ENCRYPTION_KEY)

app = Quart(__name__)

# MongoDB setup
client = AsyncIOMotorClient(DB_CONNECTION_STRING)
db = client['NoGap']
tokens_collection = db["Tokens"]

CORS(app)

@app.route('/')
def hello_world():
    return jsonify('Welcome to the KnowGap Backend API!')

# Add your new endpoint for getting video recommendations
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
    reccs = get_curated_videos.get_assessment_videos(student_id, course_id)
    print(f"Returning recommendations: {reccs}")  # Log the returned data
    return jsonify(reccs)

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

    encrypted_token = at_risk_encrypt_token(encryption_key, access_token)

    token_collection = db["Tokens"]
    token_collection.update_one({'_id': user_id},{"$set": {"auth": encrypted_token, "courseids": course_ids, "link": link}},upsert=True)

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
    
    token_collection = db["Tokens"]

    user = token_collection.find_one({'_id': userid})

    if user:
        decrypted_token = at_risk_decrypt_token(encryption_key, user['auth'])
        return jsonify({
            'status' : 'Success',
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
    questionid= data.get('questionid')
    old_link = data.get('old_link')
    new_link = data.get('new_link')

    if not all([quizid, old_link, new_link, questionid]):
        return jsonify({'error': 'Missing parameters'}), 400

    update_result = update_video_link(quizid, questionid, old_link, new_link)
    
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
    update_result = update_context(courseid, new_course_context)

    if 'error' in update_result:
        return jsonify({'error': update_result['error']}), 400
    
    return jsonify({'message': update_result['message']}), 200


if __name__ == "__main__" :
    app.run(debug=True)
