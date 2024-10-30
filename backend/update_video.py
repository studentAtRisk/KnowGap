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
db = mdb_client['KnowGap']

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

    # Fetch the document based on quiz_id and question_id
    document = quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    if not document:
        return {"message": "Document not found", "success": False}

    # Extract the video_data array (assuming it's an array of strings)
    video_data = document.get('video_data', [])

    # Check if the old_link is in the video_data array
    if old_link not in video_data:
        return {"message": "Old video not found in video_data", "success": False}

    # Remove the old link from the in-memory array
    updated_video_data = [link for link in video_data if link != old_link]

    # Add the new link (optional: add more metadata like title, thumbnail if required)
    updated_video_data.append(new_video)

    # Update the document in the database with the modified video_data array
    update_result = quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": updated_video_data}}
    )

    if update_result.modified_count == 0:
        return {"message": "Failed to update video_data", "success": False}
    return {"message": "Video successfully updated", "success": True}

def add_video(quiz_id, question_id, video_link):
    quizzes_collection = db['Quiz Questions']
    
    # Fetch the document based on quiz_id and question_id
    document = quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    # Error checking
    if not document:
        return {
            "error": "document not found",
            "success": False
        }
        
    # Getting the video data
    video_data = document.get('video_data', [])
    
    # Avoiding duplicates
    if video_link in video_data:
        return {
            "error": "Video present already",
            "success": False
        }
    
    # Add the new video in the data array...
    video_data.append(video_link)
    
    # Making the update in the db
    
    quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": video_data}}
    )
    
    return {
        "message": "Video Added",
        "success": True
    }
    
    
def remove_video(quiz_id, question_id, video_to_be_removed):
    quizzes_collection = db['Quiz Questions']
    
    # Fetch the document based on quiz_id and question_id
    document = quizzes_collection.find_one({"quizid": quiz_id, "questionid": question_id})
    
    # Error checking
    if not document:
        return {
            "error": "document not found",
            "success": False
        }
        
    # Getting the video data
    video_data = document.get('video_data', [])
    
    # Return if video is not present in db
    if video_to_be_removed not in video_data:
        return {
            "message": "Video not found",
            "success": False
        }
        
    # Reconstructing video array without video to delete (removing step)
    updated_video_data = [link for link in video_data if link != video_to_be_removed]
    
    quizzes_collection.update_one(
        {"quizid": quiz_id, "questionid": question_id},
        {"$set": {"video_data": video_data}}
    )
    
    return {
        "message": "video successfully removed",
        "success": True
    }


if __name__ == "__main__":
    mock_json = {
    "quizid": 19758187,
    "questionid": "210760403",
    "old_link": "https://www.youtube.com/watch?v=aGEFtRwPhE4",
    "new_link": "https://www.youtube.com/watch?v=EsumcNL_ujY"
    }
    update_video_link(mock_json["quizid"], mock_json["questionid"], mock_json["old_link"], mock_json["new_link"])
    quizzes_collection = db["Quiz Questions"]
