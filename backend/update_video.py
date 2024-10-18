from flask import Flask, request, jsonify  # Add this import
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
            "thumbnail": video["thumbnails"]["high"]["url"], # high = HD
            "description": video["description"]
        }
        return metadata
    else:
        return {"error": "Video not found"}

def update_video_link(quiz_id, old_link, new_link):
    """
    Function to update a specific video in the video_data array.

    :param quiz_id: The quiz ID associated with the document.
    :param old_link: The link of the video to be replaced.
    :param new_link: The new video link.
    :return: A dictionary with success or error message.
    """
    quizzes_collection = db['Quiz Questions']
    result = quizzes_collection.find_one(
    {"quizid": mock_json["quizid"], "video_data.link": mock_json["old_link"]})
    print("Found? " + str(result))
    # Retrieve metadata for the new video
    new_video_metadata = get_video_metadata(new_link)       

    print("New video metadata: " + str(new_video_metadata))

    if "error" in new_video_metadata:
        return {"error": new_video_metadata["error"]}

    # Pull removes the video with the old link
    pull_result = quizzes_collection.update_one(
        {"quizid": quiz_id},
        {"$pull": {"video_data": {"link": old_link}}}
    )

    print("Pull result: " + str(pull_result))

    if pull_result.modified_count == 0:
        return {"error": "Old video not found or already removed"}

    # Push the new video metadata into video_data
    push_result = quizzes_collection.update_one(
        {"quizid": quiz_id},
        {"$push": {"video_data": new_video_metadata}}
    )

    
    print("Push result: " + str(push_result))

    if push_result.modified_count == 0:
        return {"error": "Failed to add new video"}

    return {"success": True, "message": "Video updated successfully"}

if __name__ == "__main__":
    mock_json = {
    "quizid": "19758187",
    "old_link": "https://www.youtube.com/watch?v=VKd2ARCyqCs",
    "new_link": "https://www.youtube.com/watch?v=EsumcNL_ujY"
    }
    quizzes_collection = db["Quiz Questions"]
