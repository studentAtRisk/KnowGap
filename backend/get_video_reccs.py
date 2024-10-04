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

def print_collection(collection):
    # Fetch all documents in the collection
    documents = collection.find()
    
    # Iterate over the documents and print each one
    for document in documents:
        print(document)

# Function to get video recommendations for incorrect answers and store metadata
def get_video_recommendation_and_store():
    # Step 1: Query the database for the quiz data based on course_id and quiz_id
    # Extract the quiz info (assuming quizzes is an array inside the course document)


    # Initialize an empty dictionary to store video recommendations for each topic
    videos = {}

    # Step 2: Process each question in the quiz
    for question in quizzes_collection.find():
        question_text = question.get('question_text')
        if not question_text:
            continue  # Skip questions without text

        # Step 3: Generate a core topic for each question
        core_topic = generate_core_topic(question_text)

        # Step 4: Check if this topic already exists in `topic_links` collection
        existing_topic = topic_links_collection.find_one({'topic': core_topic})

        if existing_topic:
            # Step 5: Use existing video links if found
            video_data = existing_topic['video_data']
            print(f"Reusing stored video data for topic: {core_topic}")
        else:
            # Step 6: Fetch YouTube videos for the generated topic
            video_data = fetch_videos_for_topic(core_topic)

            # Step 7: Insert new topic and video data into topic_links collection
            print(f"Inserting new topic into topic_links: {core_topic}")
            try:
                topic_links_collection.insert_one({
                    'topic': core_topic,
                    'video_data': video_data  # Store full video data (link, channel, title, thumbnail)
                })
                print(f"Successfully inserted topic: {core_topic} into topic_links.")
            except Exception as e:
                print(f"Error inserting into topic_links: {e}")
        cur_course_id = question.get("courseid")
        cur_quiz_id = question.get("quizid")
        cur_question_id = question.get("questionid")
        # Step 8: Store the core topic and video data in MongoDB for the specific question
        quizzes_collection.update_one(
            {'questionid' : cur_question_id},
            {'$set': {
                'core_topic': core_topic,
                'video_data': video_data  # Store full video data
            }}, upsert=True
        )

        # Step 9: Store the topic and videos in the response dictionary
        videos[core_topic] = video_data

    return videos

# ================================================================================================================================================
#                                                   Helper Functions
# ================================================================================================================================================

# Function to generate a core topic using OpenAI
def generate_core_topic(question_text):
    prompt = f"Generate a concise and general core topic to study for the following question, ensuring it's easy to search on YouTube and will return the most relevant video content: {question_text}"
    response = client.completions.create(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        top_p=0.5,
        max_tokens=50,
        stream=False
    )

    # Accessing the text from the completion choices
    core_topic = response.choices[0].text.strip()
    print(f"Generated core topic: {core_topic}")  # For debugging
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
videos = get_video_recommendation_and_store()
print(videos)
