import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import get_video_reccs as get_video_reccs

load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
mongo_client = MongoClient(DB_CONNECTION_STRING)

db = mongo_client['NoGap']
students_collection = db['Students']
quizzes_collection = db['Quiz Questions']


def get_assessment_videos(student_id, course_id):
    core_topic = ""
    print("Getting assessment videos")
    
    try:
        student_record = students_collection.find_one({"_id": student_id})
    except Exception as e:
        print(f"Error fetching student record: {e}")
        return {"error": "Student not found"}
    
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
        
        videos_for_quiz = {}

        for question in incorrect_questions:
            cur_qid = question.get("questionid")
            video_for_quiz = []

            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "questionid": cur_qid})

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                video_for_quiz = matching_question.get("video_data", [])

                if core_topic == "No topic found":
                    core_topic = get_video_reccs.generate_core_topic(cur_qid, course_id)

                if not video_for_quiz:
                    video_for_quiz = get_video_reccs.fetch_videos_for_topic(core_topic)

                new_entry = {
                    "quizid": quiz_id,
                    "question_text": cur_qid,
                    "core_topic": core_topic,
                    "video_data": video_for_quiz
                }
                quizzes_collection.insert_one(new_entry)

            if core_topic is not None:
                print("Core topic: " + str(core_topic))
            else:
                print("Core topic is None")

            videos_for_quiz[cur_qid] = {
                "topic": core_topic,
                "videos": video_for_quiz
            }

        assessment_videos[quiz_name] = videos_for_quiz
    
    return assessment_videos


def get_cid_from_sid(studentid):
    try:
        student_record = students_collection.find_one({"_id": studentid})
    except Exception as e:
        print(f"Error fetching student record: {e}")
        return None

    if student_record:
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
    student_id = "113513458"
    course_id = "10431626"
    
    videos_by_assessment = get_assessment_videos(student_id, course_id)

    from pprint import pprint

    print(json.dumps(videos_by_assessment, indent=2))
