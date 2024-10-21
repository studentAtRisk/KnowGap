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

db = mongo_client['KnowGap']
students_collection = db['Students']  # Collection that stores student records
quizzes_collection = db['Quiz Questions']  # Collection that stores all possible quiz questions



# Function to get incorrect questions and their video links
def get_assessment_videos(student_id, course_id):
    core_topic = ""
    print("Getting assessment videos")
    student_record = students_collection.find_one({"_id": student_id})
    
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}

    print("Quizzes: " + str(quizzes))

    for quiz in quizzes:
        quiz_name = quiz.get('quizname', 'Unknown Quiz')
        quiz_id = quiz.get('quizid')
        incorrect_questions = quiz.get('questions', [])

        if not quiz_id:
            continue

        quiz_videos = []

        for question in incorrect_questions:
            cur_qid = question.get("questionid")
            cur_question_text = question.get('question_text')
            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "questionid": cur_qid})
            print("Matching question = " + str(matching_question))

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                videos_for_question = matching_question.get('video_data', [])
            else:
                cur_question_text = question.get('question_text')
                core_topic = get_video_reccs.generate_core_topic(cur_question_text,cur_qid, course_id)
                videos_for_question = get_video_reccs.fetch_videos_for_topic(core_topic)
            
            quiz_videos.append({
                "questionid": cur_qid,
                "topic": core_topic,
                "videos": videos_for_question
            })
            
            if not matching_question:
                new_entry = {
                    "quizid": quiz_id,
                    "questionid": cur_qid,
                    "core_topic": core_topic,
                    "video_data": videos_for_question,
                    "question_text": cur_question_text
                }
                quizzes_collection.insert_one(new_entry)

        assessment_videos[quiz_name] = quiz_videos
    
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
        

def get_course_videos(course_id):
    core_topic = ""
    print("Getting assessment videos for course:", course_id)
    
    # Query quizzes based on course_id directly
    quizzes = quizzes_collection.find({"course_id": course_id})
    if not quizzes:
        return {"error": f"No quizzes found for course: {course_id}"}
    
    assessment_videos = {}

    for quiz in quizzes:
        quiz_name = quiz.get('quizname', 'Unknown Quiz')
        quiz_id = quiz.get('quizid')
        incorrect_questions = quiz.get('questions', [])

        if not quiz_id:
            continue

        quiz_videos = []

        for question in incorrect_questions:
            cur_qid = question.get("questionid")

            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "questionid": cur_qid})
            print("Matching question = " + str(matching_question))

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                videos_for_question = matching_question.get('video_data', [])
            else:
                cur_question_text = question.get('question_text')
                core_topic = get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                videos_for_question = get_video_reccs.fetch_videos_for_topic(core_topic)
            
            quiz_videos.append({
                "questionid": cur_qid,
                "topic": core_topic,
                "videos": videos_for_question
            })
            
            if not matching_question:
                new_entry = {
                    "quizid": quiz_id,
                    "questionid": cur_qid,
                    "core_topic": core_topic,
                    "video_data": videos_for_question
                }
                quizzes_collection.insert_one(new_entry)

        assessment_videos[quiz_name] = quiz_videos
    
    return assessment_videos



if __name__ == "__main__":
# Example usage
    student_id = "113513458"  # Replace with actual student ID
    course_id = "10496761"  # Replace with actual course ID
    print("Course (?) Id is: " + str(get_cid_from_sid(student_id)))
    print("I guess we're in maine buddy")
    videos_by_assessment = get_assessment_videos(student_id, course_id)

    from pprint import pprint

    print(json.dumps(videos_by_assessment, indent=2))
