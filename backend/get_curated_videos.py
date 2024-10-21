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
students_collection = db['Students']
quizzes_collection = db['Quiz Questions']  
def is_duplicate_video(quiz_videos, questionid):
    for video in quiz_videos:
        if video["questionid"] == questionid:
            return True
    return False


def get_assessment_videos(student_id, course_id):
    core_topic = ""
    print("Getting assessment videos")
    student_record = students_collection.find_one({"_id": student_id})
    
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}

    print("Quizzes: " + str(quizzes))

    # To track used videos by topic, preventing duplicates
    used_videos_by_topic = {}

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
                core_topic = get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                videos_for_question = get_video_reccs.fetch_videos_for_topic(core_topic)
            
            # Initialize set of used videos for this topic if not already initialized
            if core_topic not in used_videos_by_topic:
                used_videos_by_topic[core_topic] = set()

            # Filter videos to avoid adding duplicates
            unique_videos = []
            for video in videos_for_question:
                if video['link'] not in used_videos_by_topic[core_topic]:
                    unique_videos.append(video)
                    used_videos_by_topic[core_topic].add(video['link'])  # Mark video as used

            # Skip if there are no unique videos
            if not unique_videos:
                continue

            # Append only if there are unique videos
            quiz_videos.append({
                "questionid": cur_qid,
                "topic": core_topic,
                "videos": unique_videos
            })

            # If the question doesn't exist in the collection, store it
            if not matching_question:
                new_entry = {
                    "quizid": quiz_id,
                    "questionid": cur_qid,
                    "core_topic": core_topic,
                    "video_data": unique_videos,
                    "question_text": cur_question_text
                }
                quizzes_collection.update_one(
                    {"quizid": quiz_id, "questionid": cur_qid}, 
                    {"$set": new_entry}, 
                    upsert=True
                )

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
