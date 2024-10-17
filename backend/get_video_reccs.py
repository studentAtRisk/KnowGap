from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, jsonify, request

load_dotenv()  # Load the environment variables

API_KEY = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=API_KEY)

# Connect to MongoDB
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

mongo_client = MongoClient(DB_CONNECTION_STRING)
db = mongo_client['NoGap']
quizzes_collection = db['Quiz Questions']
topic_links_collection = db['topic_links']  # Collection for storing topic video links

# Function to get video recommendations for incorrect answers and store metadata
def get_video_recommendation_and_store():
    videos = {}

    # Step 2: Process each question in the quiz
    for question in quizzes_collection.find():
        question_text = question.get('question_text')
        if not question_text:
            continue  

        core_topic = generate_core_topic(question_text)

        existing_topic = quizzes_collection.find_one({'topic': core_topic})

        if existing_topic:
            video_data = existing_topic['video_data']
            print(f"Reusing stored video data for topic: {core_topic}")
        else:
            video_data = fetch_videos_for_topic(core_topic)

        cur_course_id = question.get("courseid")
        cur_quiz_id = question.get("quizid")
        cur_question_id = question.get("questionid")

        #Store the core topic and video data in MongoDB for the specific question
        quizzes_collection.update_one(
            {'questionid' : cur_question_id},
            {'$set': {
                'core_topic': core_topic,
                'video_data': video_data 
            }}, upsert=True
        )

        videos[core_topic] = video_data

    return videos

# ================================================================================================================================================
#                                                   Helper Functions
# ================================================================================================================================================

# Function to generate a core topic using OpenAI
def generate_core_topic(question_text, course_id):
    prompt = (f"Based on the following question from course {course_id}, "
              f"generate a concise, specific core topic that is relevant to the subject matter. "
              f"The topic should be no longer than 4-5 words and should directly relate to the main concepts: {question_text}")

    response = client.completions.create(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        top_p=0.5,
        max_tokens=50,
        stream=False
    )

    # Accessing the text from the completion choices
    core_topic = response.choices[0].text.strip()
    print(f"Generated core topic: {core_topic}")  
    return core_topic


# Function to fetch YouTube videos for a given topic and return video data (link, title, channel, thumbnail)
def fetch_videos_for_topic(topic):
    try:
        search = VideosSearch(topic, limit=2)
        search_results = search.result()['result']
        video_data = []

        # Extract required information from each video
        for video in search_results:
            video_info = {
                'link': video['link'],
                'title': video['title'],
                'channel': video['channel']['name'],
                'thumbnail': video['thumbnails'][0]['url']
            }
            video_data.append(video_info)

        return video_data
    except Exception as e:
        print(f"Error fetching videos for topic '{topic}': {e}")
        return []

# Fetch video recommendations for all questions in a quiz and store them
if __name__ == "main":
    videos = get_video_recommendation_and_store()
    print(videos)
