import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
import get_video_reccs as get_video_reccs  # Ensure correct import of external functions
# Load environment variables
load_dotenv()

# MongoDB connection
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
mongo_client = MongoClient(DB_CONNECTION_STRING)

db = mongo_client['NoGap']
students_collection = db['Students']  # Collection that stores student records
quizzes_collection = db['Quiz Questions']  # Collection that stores all possible quiz questions



# Function to get incorrect questions and their video links
def get_assessment_videos(student_id, course_id):
    # Fetch student's quizzes based on course_id
    print("Getting assessment videos")
    student_record = students_collection.find_one({"_id": student_id})
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}

    print("Quizzes: " + str(quizzes))
    # Iterate over each quiz the student took in the specified course
    for quiz in quizzes:
        quiz_name = quiz.get('quizname', 'Unknown Quiz')  # Added default value in case 'quizname' is missing
        quiz_id = quiz.get('quizid')
        incorrect_questions = quiz.get('questions', [])

        if not quiz_id:
            continue  # Skip if quiz ID is missing
        
        videos_for_quiz = {}

        # For each incorrect question, we match it with the corresponding question in the `Quiz Questions` collection
        for question in incorrect_questions:
            # Clean the question text of unwanted characters
            cur_qid = question.get("questionid")

            # Find the matching question in the `Quiz Questions` collection
            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "questionid": cur_qid})
            
            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                video_data = matching_question.get("video_data", [])
            if core_topic == "No topic found":
                core_topic = get_video_reccs.generate_core_topic(cur_qid, course_id)      
            
            if not video_data:
                video_data = get_video_reccs.fetch_videos_for_topic(core_topic)
                new_entry = {
                    "quizid": quiz_id,
                    "question_text": cur_qid,
                    "core_topic": core_topic,
                    "video_data": video_data
                }
                quizzes_collection.insert_one(new_entry)

            print("Core topic: " + str(core_topic))

            # Store the video data by question
            videos_for_quiz[cur_qid] = {
                "topic": core_topic,
                "videos": video_data
            }
        # Group by assessment (quiz)
        assessment_videos[quiz_name] = videos_for_quiz
    
    return assessment_videos

def get_cid_from_sid(studentid):
    student_record = students_collection.find_one({"_id": student_id})

    if student_record:
        # Assume that we want to extract the top-level key in the student's data hierarchy
        # Loop over the keys in the document and skip MongoDB's default '_id' key
        top_level_key = None
        for key in student_record:
            print("Cur key = " + str(key))
            if key != '_id':
                top_level_key = key
                return key

        if top_level_key:
            print(f"The top-level key is: {top_level_key}")
        else:
            print("No top-level key found.")
    else:
        print("Student not found.")
        
if __name__ == "__main__":
# Example usage
    student_id = "113513458"  # Replace with actual student ID
    course_id = "10431626"  # Replace with actual course ID
    print("Course (?) Id is: " + str(get_cid_from_sid(student_id)))
    print("I guess we're in maine buddy")
    videos_by_assessment = get_assessment_videos(student_id, course_id)

    from pprint import pprint

    print(json.dumps(videos_by_assessment, indent=2))
