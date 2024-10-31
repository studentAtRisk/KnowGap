import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import asyncio
import get_video_reccs  # Ensure correct import of external functions

# Load environment variables
load_dotenv()

# MongoDB connection
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
mongo_client = MongoClient(DB_CONNECTION_STRING)

db = mongo_client['KnowGap']
students_collection = db['Students']
quizzes_collection = db['Quiz Questions']

# Function to get incorrect questions and their video links
async def get_assessment_videos(student_id, course_id):
    print("Getting assessment videos")
    student_record = students_collection.find_one({"_id": student_id})
    
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}
    used_video_links = set()

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
                core_topic = await get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                videos_for_question = await get_video_reccs.fetch_videos_for_topic(core_topic)

            unique_videos = [video for video in videos_for_question if video['link'] not in used_video_links]
            used_video_links.update(video['link'] for video in unique_videos)
            
            if unique_videos:
                quiz_videos.append({
                    "questionid": cur_qid,
                    "topic": core_topic,
                    "videos": unique_videos
                })

        if quiz_videos:
            assessment_videos[quiz_name] = quiz_videos

    return assessment_videos

# Function to get course ID from a student record
def get_cid_from_sid(student_id):
    student_record = students_collection.find_one({"_id": student_id})

    if student_record:
        for key in student_record:
            if key != '_id':
                print(f"The top-level key is: {key}")
                return key
    else:
        print("Student not found.")
    return None

# Function to get videos by course
async def get_course_videos(course_id):
    print("Getting assessment videos for course:", course_id)
    quizzes = quizzes_collection.find({"course_id": course_id})
    
    if quizzes.count() == 0:
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

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                videos_for_question = matching_question.get('video_data', [])
            else:
                cur_question_text = question.get('question_text')
                core_topic = await get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                videos_for_question = await get_video_reccs.fetch_videos_for_topic(core_topic)

            unique_videos = [video for video in videos_for_question if video['link'] not in used_videos]
            used_videos.update(video['link'] for video in unique_videos)
            
            if unique_videos:
                quiz_videos.append({
                    "questionid": cur_qid,
                    "topic": core_topic,
                    "videos": unique_videos
                })

        if quiz_videos:
            assessment_videos[quiz_name] = quiz_videos

    return assessment_videos

# Main block to execute the async function
async def main():
    student_id = "113513458"  # Replace with actual student ID
    course_id = "10496761"  # Replace with actual course ID

    course_key = get_cid_from_sid(student_id)
    print("Course ID obtained:", course_key)
    
    videos_by_assessment = await get_assessment_videos(student_id, course_id)
    print(json.dumps(videos_by_assessment, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
