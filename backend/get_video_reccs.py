from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, jsonify, request

load_dotenv()

API_KEY = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=API_KEY)

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

mongo_client = MongoClient(DB_CONNECTION_STRING)
db = mongo_client['NoGap']
quizzes_collection = db['Quiz Questions']
topic_links_collection = db['topic_links']

def get_video_recommendation_and_store():
    videos = {}

    for question in quizzes_collection.find():
        question_text = question.get('question_text')
        cur_video_data = question.get('video_data')
        if not question_text or question.get('video_data'):
            continue  
        
        course_name = ""
        if question.get('courseid') == '10496761': 
            course_name = "Public Speaking"
        
        course_context = question.get('course_context', "")
        
        core_topic = generate_core_topic(question_text, course_name, course_context)

        existing_topic = quizzes_collection.find_one({'core_topic': core_topic})

        if existing_topic:
            video_data = existing_topic['video_data']
            print(f"Reusing stored video data for topic: {core_topic}")
        else:
            video_data = fetch_videos_for_topic(core_topic)
        
        cur_question_text = question.get("question_text")
        cur_course_name = question.get("course_name")
        cur_course_id = question.get("courseid")
        cur_quiz_id = question.get("quizid")
        cur_question_id = question.get("questionid")

        quizzes_collection.update_one(
            {
                'questionid': cur_question_id,
                'course_name': cur_course_name,
                'courseid': cur_course_id,
                'quizid': cur_quiz_id,
                'question_text': cur_question_text
            },
            {
                '$set': {
                    'core_topic': core_topic,
                    'video_data': video_data,
                    'course_context': course_context
                }
            },
            upsert=True
        )

        videos[core_topic] = video_data

    return videos

def generate_core_topic(question_text, course_name, course_context=""):
    prompt = (f"Based on the following question from course {course_name}, "
              f"generate a concise, specific core topic that is relevant to the subject matter. "
              f"The topic should be no longer than 4-5 words and should directly relate to the main concepts: {question_text}")
    
    if course_context:
        prompt += (f"\nHere's what the instructor gave us, so use it to generate a more relevant topic in the context of the course itself: {course_context}")

    response = client.completions.create(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        top_p=0.5,
        max_tokens=50,
        stream=False
    )

    core_topic = response.choices[0].text.strip()
    print(f"Generated core topic: {core_topic}")  
    return core_topic

def fetch_videos_for_topic(topic):
    try:
        search = VideosSearch(topic, limit=1)
        search_results = search.result()['result']
        video_data = []

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

if __name__ == "__main__":
    videos = get_video_recommendation_and_store()
    print(videos)
