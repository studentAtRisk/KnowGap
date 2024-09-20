# Come back and import the stuff here
from youtubesearchpython import VideosSearch
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=API_KEY)

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Jason!'

@app.route('/getvideorec')
def get_video_recommendation(): # ==== Add in async
    student_data = request.get_json() # Get Quiz info
    
    topics_final =  process_student(student_data) # Put in await
    
    query =  generate_core_topic(topics_final) # Put in await
    
    print(f"Query is: {query}")
    
    # Check if query is a string or list and process accordingly
    if isinstance(query, str):
        query = query.splitlines()
        
    print(f"Query after conversion is: {query}")
        
    
    print(f"Second Debugging print: {type(query)}")
        
    # Now clean up each topic by removing index numbers and unnecessary whitespace
    topic_list = [item.split(". ", 1)[1] if ". " in item else item for item in query]
    cleaned_topics = [item for item in topic_list if item.strip()]  # Remove any empty or whitespace-only entries
    
    topic_list =  [item.split(". ", 1)[1] if ". " in item else item for item in query]
    cleaned_topics = [item for item in topic_list if item.strip()]
    
    videos = {}
    for topic in cleaned_topics:
        if topic:
            cur_search = fetch_videos_for_topic(topic)
            cur_videos = json.dumps(cur_search.result())
        videos[topic] = cur_videos
    return jsonify(videos)

# ================================================================================================================================================
#                                                   Passed this bridge, we go in helper functions land
# ================================================================================================================================================
# Beyond this point, those functions are helper function
# Function to generate a core topic using OpenAI
def generate_core_topic(question_data): # ==== Add in async
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
    print(core_topic) #testing purposes
    return core_topic

# Function to generate a YouTube query using OpenAI
def generate_youtube_query(topic): # ==== Add in async
    prompt = f"Generate a broad YouTube search query for the topic: {topic}."
    
    # Generating completion using OpenAI client
    response = client.completions.create(
        prompt=prompt,
        model="gpt-3.5-turbo-instruct",
        top_p=0.5,
        max_tokens=50,
        stream=False
    )
    
    # Accessing the text from the completion choices
    youtube_query = response.choices[0].text.strip()
    return youtube_query

# Function to process each student's data
def process_student(student_data): # ==== Add in async
    topics = [question['question'] for question in student_data['questions']]
    return topics

def fetch_videos_for_topic(topic):
    try:
        search = VideosSearch(topic, limit=2)
        return search
    except Exception as e:
        print(f"Error fetching videos for topic '{topic}': {e}")
        return None

if __name__ == "__main__":
    app.run()