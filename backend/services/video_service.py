# services/video_service.py

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from utils.youtube_utils import fetch_video_for_topic
from utils.ai_utils import generate_core_topic
from config import Config

# Load environment variables
load_dotenv()

# MongoDB async connection
mongo_client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)

db = mongo_client[Config.DATABASE]
students_collection = db[Config.STUDENTS_COLLECTION]
quizzes_collection = db[Config.QUIZZES_COLLECTION]
contexts_collection = db[Config.COURSES_COLLECTION]  # For course context data

async def get_assessment_videos(student_id, course_id):
    """Retrieve incorrect questions and associated video links for assessments."""
    student_record = await students_collection.find_one({"_id": student_id})
    if not student_record:
        return {"error": "Student not found"}

    quizzes = student_record.get(course_id, [])
    assessment_videos = []
    used_video_links = set()

    for quiz in quizzes:
        quiz_name = quiz.get('quizname', 'Unknown Quiz')
        quiz_id = quiz.get('quizid')
        incorrect_questions = quiz.get('questions', [])

        for question in incorrect_questions:
            question_data = await quizzes_collection.find_one({"quizid": quiz_id, "questionid": question.get("questionid")})
            if question_data:
                core_topic = question_data.get("core_topic", "No topic found")
                video_data = question_data.get('video_data')  # Expecting a single video dictionary, not a list
                
                if video_data and video_data['link'] not in used_video_links:
                    used_video_links.add(video_data['link'])
                    assessment_videos.append({
                        "quiz_name": quiz_name,
                        "question_id": question.get("questionid"),
                        "question_text": question.get("question_text"),
                        "topic": core_topic,
                        "video": video_data  # Store a single video dictionary
                    })

    return assessment_videos

async def get_course_videos(course_id):
    """Fetch all video data associated with a specific course ID."""
    course_videos = []
    async for quiz in quizzes_collection.find({"courseid": course_id}):
        video_data = quiz.get('video_data')
        core_topic = quiz.get('core_topic')
        question_text = quiz.get('question_text')
        
        if video_data:
            course_videos.append({
                'core_topic': core_topic,
                'question_text': question_text,
                'video_data': video_data
            })
    return course_videos

async def update_videos_for_filter(filter_criteria=None):
    """Update videos for all questions that match the filter criteria."""
    query = filter_criteria if filter_criteria else {}
    async for question in quizzes_collection.find(query):
        question_text = question.get('question_text')
        if not question_text or question.get('video_data'):
            continue

        course_id = question.get('courseid')
        course_name = question.get('course_name', "")

        # Fetch context data and core topic
        course_context_data = await contexts_collection.find_one({'courseid': course_id})
        course_context = course_context_data.get('course_context', "") if course_context_data else ""
        core_topic = await generate_core_topic(question_text, course_name, course_context)

        # Fetch or update video data for the topic
        video_data = await fetch_videos_for_topic(core_topic)

        await quizzes_collection.update_one(
            {'questionid': question.get("questionid")},
            {'$set': {'core_topic': core_topic, 'video_data': video_data, 'course_context': course_context}},
            upsert=True
        )

    return {"message": "Videos updated successfully"}

async def update_course_videos(course_id):
    """Updates videos for all questions within a specific course ID."""
    filter_criteria = {'courseid': course_id}
    return await update_videos_for_filter(filter_criteria)
