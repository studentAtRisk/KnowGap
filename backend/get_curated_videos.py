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
async def get_assessment_videos(student_id, course_id):
    core_topic = ""
    print("Getting assessment videos")
    student_record = students_collection.find_one({"_id": student_id})
    
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}

    print("Quizzes: " + str(quizzes))

    used_video_links = set()  # Set to track unique video links

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

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                videos_for_question = matching_question.get('video_data', [])
            else:
                core_topic = get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                videos_for_question = await get_video_reccs.fetch_videos_for_topic(core_topic)

            unique_videos = []
            for video in videos_for_question:
                if video['link'] not in used_video_links:
                    unique_videos.append(video)
                    used_video_links.add(video['link']) 
            
            if unique_videos:
                quiz_videos.append({
                    "questionid": cur_qid,
                    "topic": core_topic,
                    "videos": unique_videos
                })

        if quiz_videos:
            assessment_videos[quiz_name] = quiz_videos

    return assessment_videos


def get_cid_from_sid(studentid):
    student_record = students_collection.find_one({"_id": student_id})

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
        

async def get_course_videos(course_id):
    core_topic = ""
    print("Getting assessment videos for course:", course_id)
    
    quizzes = quizzes_collection.find({"course_id": course_id})
    if not quizzes:
        return {"error": f"No quizzes found for course: {course_id}"}
    
    assessment_videos = {}
    used_videos = set()  

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

            unique_videos = []
            for video in videos_for_question:
                if video['link'] not in used_videos:
                    unique_videos.append(video)
                    used_videos.add(video['link']) 
            
            if unique_videos:
                quiz_videos.append({
                    "questionid": cur_qid,
                    "topic": core_topic,
                    "videos": unique_videos
                })

        if quiz_videos: 
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