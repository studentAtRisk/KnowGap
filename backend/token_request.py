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
db = client['NoGap']  
collection_name = db['Tokens']  


# POST endpoint to update or create a user
@app.route('/update_user_auth', methods=['POST'])
def update_course_request_endpoint():
    data = request.get_json()

    userid = data.get('userid')
    access_token = data.get('access_token')
    role = data.get('role')
    courseids = data.get('courseids')

    # validate required parameters
    if not all([userid]):
        return jsonify({'error': 'Missing userid'}), 400


    if role == "student":
        collection_name.update_one({'_id': userid},{"$set": {"auth": access_token, "role": role}},upsert=True)
    else:
        collection_name.update_one({'_id': userid},{"$set": {"auth": access_token, "role": role, "courseids": courseids}},upsert=True)


    # return updated user details
    updated_user = collection_name.find_one({'_id': userid}, {'_id': 0})  # Exclude _id in the result
    if updated_user:
        return jsonify({'status': 'Complete', 'user_details': updated_user})
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404



# GET endpoint to retrieve user data
@app.route('/get_user', methods=['GET'])
def get_user():
    # get the userid from query parameters (e.g., /get_user?userid=123)
    userid = request.args.get('userid')

    if not userid:
        return jsonify({'error': 'Missing userid parameter'}), 400

    # fetch the user from MongoDB
    user = collection_name.find_one({'_id': userid}, {'_id': 0})  # Exclude _id in the result

    if user:
        return jsonify({'status': 'Success', 'user_details': user})
    else:
        return jsonify({'status': 'Error', 'message': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)