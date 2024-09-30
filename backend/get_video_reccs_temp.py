from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient

load_dotenv()  # Load the environment variables

API_KEY = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=API_KEY)
DB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')


def get_video_recommendation(student_data):
    # Process the student data to extract topics
    topics_final = process_student(student_data)
    query = generate_core_topic(topics_final)

    # Check if query is a string or list and process accordingly
    if isinstance(query, str):
        query = query.splitlines()

    # Clean up each topic by removing index numbers and unnecessary whitespace
    topic_list = [item.split(". ", 1)[1] if ". " in item else item for item in query]
    cleaned_topics = [item for item in topic_list if item.strip()]  # Remove any empty or whitespace-only entries

    videos = {}
    for topic in cleaned_topics:
        if topic:
            cur_search = fetch_videos_for_topic(topic)
            cur_videos = json.dumps(cur_search.result())
            videos[topic] = cur_videos
    return videos


# ================================================================================================================================================
#                                                   Passed this bridge, we go in helper functions land
# ================================================================================================================================================

# Function to generate a core topic using OpenAI
def generate_core_topic(question_data):
    prompt = f"From the following question and answer data, extract a unique core topic from each question to study: {question_data}"
    response = client.completions.create(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        top_p=0.5,
        max_tokens=50,
        stream=False
    )

    # Accessing the text from the completion choices
    core_topic = response.choices[0].text.strip()
    print(core_topic)  # testing purposes
    return core_topic


# Function to process each student's data
def process_student(student_data):
    topics = []

    # Loop through each quiz in student data
    for quiz in student_data:
        quizname = quiz['quizname']
        questions = quiz['questions']  # Expecting this to be an array of strings

        # Add each question to the topics list
        topics.extend(questions)  # Extends the list with strings directly

    return topics


def fetch_videos_for_topic(topic):
    try:
        search = VideosSearch(topic, limit=2)
        return search
    except Exception as e:
        print(f"Error fetching videos for topic '{topic}': {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Sample student data
    student_data_example = [
        {
            "quizname": "Quiz 1",
            "questions": [
                "What is the capital of France?",
                "What is 2 + 2?"
            ]
        },
        {
            "quizname": "Quiz 2",
            "questions": [
                "What is the square root of 16?",
                "What is the chemical symbol for water?"
            ]
        }
    ]

    recommendations = get_video_recommendation(student_data_example)
    print(recommendations)