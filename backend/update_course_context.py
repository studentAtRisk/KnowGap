from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

mdb_client = MongoClient(DB_CONNECTION_STRING)
db = mdb_client['NoGap']

def update_context(course_id, course_context):
    try:
        # Connect to MongoDB
        course_context_collection = db['Course Contexts']

        # Update or insert the course context
        course_context_collection.update_one(
            {'courseid': course_id},
            {
                '$set': {
                    'courseid': course_id,
                    'course_context': course_context,
                }
            },
            upsert=True  # Create a new document if it doesn't exist
        )
        return {'status': 'Success', 'message': 'Course context updated successfully'}
    except Exception as e:
        return {'status': 'Error', 'message': str(e)}



if __name__ == "__main__":
    app.run(debug=True)
