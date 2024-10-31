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
    print("Starting assessment video retrieval")
    student_record = students_collection.find_one({"_id": student_id})
    
    if not student_record:
        print("Error: Student not found")
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
            
            # Retrieve question data from quizzes collection
            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "questionid": cur_qid})

            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                videos_for_question = matching_question.get('video_data', [])
            else:
                # Await both core topic generation and video fetching
                print(f"Generating core topic for question: {cur_question_text}")
                core_topic = await get_video_reccs.generate_core_topic(cur_question_text, cur_qid, course_id)
                
                print(f"Fetching videos for topic: {core_topic}")
                videos_for_question = await get_video_reccs.fetch_videos_for_topic(core_topic)
                print(f"Fetched videos: {videos_for_question}")

            # Ensure videos are JSON-serializable and unique
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

    print("Assessment videos retrieved successfully")
    return assessment_videos

async def get_course_videos(course_id):
    try:
        # Define a query to fetch all quizzes associated with the given course_id
        query = {'courseid': course_id}

        # Count documents to check if any videos are available
        total_documents = await quizzes_collection.count_documents(query)
        if total_documents == 0:
            print(f"No videos found for course with ID: {course_id}")
            return {'status': 'Error', 'message': 'No videos found for this course ID'}

        # Initialize a list to collect video data
        course_videos = []

        # Fetch each quiz question matching the course_id and retrieve its video data
        async for quiz in quizzes_collection.find(query):
            video_data = quiz.get('video_data')
            core_topic = quiz.get('core_topic')
            question_text = quiz.get('question_text')
            
            # Add only entries with valid video data
            if video_data:
                course_videos.append({
                    'core_topic': core_topic,
                    'question_text': question_text,
                    'video_data': video_data
                })

        # Return the list of videos without a status
        return course_videos

    except Exception as e:
        return {'status': 'Error', 'message': str(e)}

# Main block to execute the async function
async def main():
    student_id = "113513458"  # Replace with actual student ID
    course_id = "10496761"  # Replace with actual course ID

    videos_by_assessment = await get_assessment_videos(student_id, course_id)
    print("Final assessment video output:")
    print(json.dumps(videos_by_assessment, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
