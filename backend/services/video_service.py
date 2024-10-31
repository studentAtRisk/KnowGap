# services/video_service.py

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from utils.youtube_utils import fetch_video_for_topic, extract_video_id, get_video_metadata
from utils.ai_utils import generate_core_topic
from config import Config

# Load environment variables
load_dotenv()

# MongoDB async connection
mongo_client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)

db = mongo_client[Config.DATABASE]
students_collection = db[Config.STUDENTS_COLLECTION]
quizzes_collection = db[Config.QUIZZES_COLLECTION]
contexts_collection = db[Config.CONTEXTS_COLLECTION]  # For course context data

async def get_assessment_videos(student_id, course_id):
    """Retrieve incorrect questions and associated video links for assessments."""
    student_record = await students_collection.find_one({"_id": student_id})
    if not student_record:
        return {"error": "Student not found"}

    quizzes = student_record.get(course_id, [])
    used_video_links = set()
    video_data_new = {}

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
                    video_data_new = ({
                        "quiz_name": quiz_name,
                        "question_id": question.get("questionid"),
                        "question_text": question.get("question_text"),
                        "topic": core_topic,
                        "video": video_data  # Store a single video dictionary
                    })

    return video_data_new

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
        
        core_topic_obj = await generate_core_topic(question_text, course_name, course_context)
        core_topic = core_topic_obj["core_topic"]
        # Fetch or update video data for the topic
        video_data = await fetch_video_for_topic(core_topic)

        
        await quizzes_collection.update_one(
            {'questionid': question.get("questionid")},
            {'$set': {'core_topic': core_topic, 'video_data': video_data, 'course_context': course_context}},
            upsert=True
        )

    return {"message": "success"}

async def update_course_videos(course_id):
    """Updates videos for all questions within a specific course ID."""
    filter_criteria = {'courseid': course_id}
    return await update_videos_for_filter(filter_criteria)


async def update_video_link(quiz_id, question_id, old_link, new_video_url):
    """Updates a specific video link within the video's data for a question."""

    # Fetch document
    document = await quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    if not document:
        return {"message": "Document not found", "success": False}

    # Get existing video data
    video_data = document.get('video_data', [])
    
    # Find the old link and remove it if present
    video_ids = [extract_video_id(link['link']) for link in video_data if 'link' in link]
    old_video_id = extract_video_id(old_link)

    if old_video_id not in video_ids:
        return {"message": "Old video not found", "success": False}

    # Create updated video metadata using new link
    new_video_metadata = await get_video_metadata(new_video_url)
    if "error" in new_video_metadata:
        return {"message": "Failed to fetch metadata for the new video", "success": False}

    # Remove old video and add new video metadata
    updated_video_data = [video for video in video_data if extract_video_id(video['link']) != old_video_id]
    updated_video_data.append(new_video_metadata)

    # Update database
    update_result = await quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": updated_video_data}}
    )

    return {
        "message": "Video successfully updated" if update_result.modified_count > 0 else "Failed to update video_data",
        "success": update_result.modified_count > 0
    }

async def add_video(quiz_id, question_id, video_link):
    """Adds a new video link and metadata to a question, avoiding duplicates."""
    
    document = await quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    if not document:
        return {"message": "Document not found", "success": False}

    video_data = document.get('video_data', [])

    # Check for duplicates by video ID
    video_ids = [extract_video_id(link['link']) for link in video_data if 'link' in link]
    new_video_id = extract_video_id(video_link)

    if new_video_id in video_ids:
        return {"message": "Video already present", "success": False}

    # Add new video metadata
    new_video_metadata = await get_video_metadata(video_link)
    if "error" in new_video_metadata:
        return {"message": "Failed to fetch metadata for the video", "success": False}

    video_data.append(new_video_metadata)

    # Update document
    await quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": video_data}}
    )
    
    return {"message": "Video added successfully", "success": True}

async def remove_video(quiz_id, question_id, video_to_be_removed):
    """Removes a specific video by link from a question's video data."""

    document = await quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    if not document:
        return {"message": "Document not found", "success": False}

    video_data = document.get('video_data', [])
    
    # Check if video exists by ID
    video_ids = [extract_video_id(link['link']) for link in video_data if 'link' in link]
    remove_video_id = extract_video_id(video_to_be_removed)

    if remove_video_id not in video_ids:
        return {"message": "Video not found", "success": False}

    # Remove video and update document
    updated_video_data = [video for video in video_data if extract_video_id(video['link']) != remove_video_id]

    await quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": updated_video_data}}
    )
    
    return {"message": "Video successfully removed", "success": True}