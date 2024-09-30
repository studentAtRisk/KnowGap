from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from get_video_reccs_temp import get_video_recommendation

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB connection
mongodb_uri = os.getenv('CONNECTIONSTRING')
client = MongoClient(mongodb_uri)

# POST endpoint to update or create a user
@app.route('/process_questions', methods=['POST'])
def update_course_request_endpoint():
    data = request.get_json()

    userid = data.get('userid')
    courseid = data.get('courseid')

    # Validate required parameters
    if not all([userid, courseid]):
        return jsonify({'error': 'Missing parameters. Need userid and courseid'}), 400

    db = client["Courses"]  
    collection_name = db[courseid]

    # Return updated user details
    found_user = collection_name.find_one({'_id': userid}, {'_id': 0})  # Exclude _id in the result

    if found_user is not None:  # Check if found_user is not None
        videos = get_video_recommendation(found_user["failed_questions"])  # Correct access
        collection_name.update_one({'_id': userid}, {"$set": {"remedial videos": videos}}, upsert=True)
        return jsonify({'status': 'Success', 'message': 'Users videos have been processed'})
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
