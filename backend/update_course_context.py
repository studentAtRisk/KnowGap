from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

mdb_client = MongoClient(DB_CONNECTION_STRING)
db = mdb_client['NoGap']

@app.route('/update_course_context', methods=['POST'])
def update_course_context():
    data = request.get_json()
    course_id = data.get('courseid')
    new_course_context = data.get('course_context', "")

    if not course_id:
        return jsonify({'error': 'courseid is required'}), 400

    try:
        result = db['Quiz Questions'].update_many(
            {
                'courseid': course_id,
                'course_context': {'$ne': new_course_context}
            },
            {
                '$set': {
                    'course_context': new_course_context
                }
            }
        )
        return jsonify({'matched_count': result.matched_count, 'modified_count': result.modified_count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
