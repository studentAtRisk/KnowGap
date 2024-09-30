from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB connection
mongodb_uri = os.getenv('CONNECTIONSTRING')
client = MongoClient(mongodb_uri)
db = client['Courses']  




# GET endpoint to retrieve user data
@app.route('/get_remedial_videos', methods=['GET'])
def get_user():
    # get the userid from query parameters (e.g., /get_user?userid=123)
    data = request.get_json()
    userid = data.get('userid')
    courseid = data.get('courseid')

    # Validate required parameters
    if not all([userid, courseid]):
        return jsonify({'error': 'Missing parameters. Need userid and courseid'}), 400

    # fetch the user from MongoDB

    collection_name = db[courseid]  
    user = collection_name.find_one({'_id': userid})  # Exclude _id in the result
    print(user)
    print("here son")

    if user:
        return jsonify({'status': 'Success', 'user_details': user["remedial videos"]})
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)