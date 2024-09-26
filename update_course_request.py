from flask import Flask, request, jsonify
from UpdateCourses import *
from pymongo import MongoClient

app = Flask(__name__)



@app.route('/update_course_request', methods=['POST'])
def update_course_request_endpoint():
    data = request.get_json()
    
    courseid = data.get('courseid')
    access_token = data.get('access_token')
    authkey = data.get('authkey')


    # Make sure there is no missing parameters from request
    if not all([courseid, access_token, authkey]):
        return jsonify({'error': 'Missing parameters'}), 400
    updatedb(courseid, access_token, authkey)

    return jsonify({'status': "Complete"})

if __name__ == '__main__':
    app.run(debug=True)