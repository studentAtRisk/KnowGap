import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
import get_video_reccs as get_video_reccs  # Ensure correct import of external functions
from sentence_transformers import SentenceTransformer, util

# Load environment variables
load_dotenv()

def normalize_text(text):
    """
    Function to normalize a given string by removing extra spaces and 
    converting it to lowercase to ensure uniformity.
    """
    # Remove extra spaces, newlines, and tabs, and convert to lowercase
    normalized_text = re.sub(r'\s+', ' ', text).strip().lower()
    return normalized_text

# Function to remove escape sequences and non-ASCII characters
def clean_text(text):
    """
    Function to remove escape sequences and non-ASCII characters from a given string.
    """
    # Remove escape sequences like \u00a0
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    
    # Remove non-ASCII characters (replace them with space or '')
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return cleaned_text


# MongoDB connection
DB_CONNECTION_STRING = 'mongodb+srv://Jason:uJ3gkMl0rmG75c55@studentsatrisk.ptqdmcu.mongodb.net/'  # This should ideally be loaded from .env
mongo_client = MongoClient(DB_CONNECTION_STRING)
db = mongo_client['NoGap']
students_collection = db['Students']  # Collection that stores student records
quizzes_collection = db['Quiz Questions']  # Collection that stores all possible quiz questions



# Function to get incorrect questions and their video links
def get_assessment_videos(student_id, course_id):
    # Fetch student's quizzes based on course_id
    student_record = students_collection.find_one({"_id": student_id})
    if not student_record:
        return {"error": "Student not found"}
    
    quizzes = student_record.get(course_id, [])
    assessment_videos = {}

    # Iterate over each quiz the student took in the specified course
    for quiz in quizzes:
        print("entering quiz loop")
        quiz_name = quiz.get('quizname', 'Unknown Quiz')  # Added default value in case 'quizname' is missing
        quiz_id = quiz.get('quizid')
        incorrect_questions = quiz.get('questions', [])

        if not quiz_id:
            continue  # Skip if quiz ID is missing
        
        videos_for_quiz = {}

        # For each incorrect question, we match it with the corresponding question in the `Quiz Questions` collection
        for question_text in incorrect_questions:
            # Clean the question text of unwanted characters
            question_text = clean_text(question_text)

            # Find the matching question in the `Quiz Questions` collection
            matching_question = quizzes_collection.find_one({"quizid": quiz_id, "question_text": question_text})
            print("Matching question: " + str(matching_question))
            if matching_question:
                core_topic = matching_question.get("core_topic", "No topic found")
                video_data = matching_question.get("video_data", [])
            else:
                # If no matching question is found, generate core topic and fetch videos
                core_topic = get_video_reccs.generate_core_topic(question_text, "EEL3801C-23Spring 0M01")      
                video_data = get_video_reccs.fetch_videos_for_topic(core_topic)
                new_entry = {
                "quizid": quiz_id,
                "question_text": question_text,
                "core_topic": core_topic,
                "video_data": video_data
                }
                quizzes_collection.insert_one(new_entry)
                print(f"Inserted new topic: {core_topic}")

            # Store the video data by question
            videos_for_quiz[question_text] = {
                "topic": core_topic,
                "videos": video_data
            }
        # Group by assessment (quiz)
        assessment_videos[quiz_name] = videos_for_quiz
    
    return assessment_videos




print("Starting BS")
# Example usage
student_id = "4365470"  # Replace with actual student ID
course_id = "1425706"  # Replace with actual course ID

videos_by_assessment = get_assessment_videos(student_id, course_id)

from pprint import pprint

print(json.dumps(videos_by_assessment, indent=2))
