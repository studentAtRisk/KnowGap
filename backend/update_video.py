from flask import Flask, request, jsonify
from pymongo import MongoClient
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

mdb_client = MongoClient(DB_CONNECTION_STRING)
db = mdb_client['NoGap']

def extract_video_id(youtube_url):
    video_id = None
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, youtube_url)
    if match:
        video_id = match.group(1)
    return video_id

def get_video_metadata(youtube_url):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video = response["items"][0]["snippet"]
        metadata = {
            "title": video["title"],
            "channel": video["channelTitle"],
            "thumbnail": video["thumbnails"]["high"]["url"],
        }
        return metadata
    else:
        return {"error": "Video not found"}

def update_video_link(quiz_id, question_id, old_link, new_video):
    quizzes_collection = db['Quiz Questions']

    document_before = quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    print("Before update: ", document_before)

    video_exists = quizzes_collection.find_one({
        "quizid": quiz_id,
        "questionid": question_id, 
        "video_data.link": old_link
    })

    if not video_exists:
        return {"error": "Old video not found in video_data"}

    pull_result = quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$pull": {"video_data": {"link": old_link}}}
    )

    print(str(pull_result))

    if pull_result.modified_count == 0:
        return {"error": "Old video not found or already removed"}

    push_result = quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$push": {"video_data": new_video}}
    )

    print("Push result: ", push_result.modified_count)

    document_after = quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    print("After update: ", document_after)

    return {"success": True}

if __name__ == "__main__":
    mock_json = {
    "quizid": 19758187,
    "questionid": "210760403",
    "old_link": "https://www.youtube.com/watch?v=aGEFtRwPhE4",
    "new_link": "https://www.youtube.com/watch?v=EsumcNL_ujY"
    }
    update_video_link(mock_json["quizid"], mock_json["questionid"], mock_json["old_link"], mock_json["new_link"])
    quizzes_collection = db["Quiz Questions"]
