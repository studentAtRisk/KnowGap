from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
import json

def extract_video_id(youtube_url):
    video_id = None
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, youtube_url)
    if match:
        video_id = match.group(1)
    return video_id

def get_video_metadata(youtube_url, api_key):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    
    youtube = build('youtube', 'v3', developerKey=api_key)

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

def update_video_link(quiz_id, old_link, new_video):
    """
    Function to update a specific video in the video_data array.

    :param quiz_id: The quiz ID associated with the document.
    :param old_link: The link of the video to be replaced.
    :param new_video: A dictionary with the new video details (link, title, thumbnail, etc.).
    """
    client = MongoClient(os.getenv('DB_CONNECTION_STRING'))
    db = client['NoGap']
    quizzes_collection = db['Quiz Questions']

    api_key = os.getenv("YOUTUBE_API_KEY")
    metadata = get_video_metadata(youtube_url, api_key)

    # pull removes the video with the old link
    quizzes_collection.update_one(
        {"quizid": quiz_id},
        {"$pull": {"video_data": {"link": old_link}}} 
    )

    quizzes_collection.update_one(
        {"quizid": quiz_id},
        {"$push": {"video_data": new_video}} 
    )

    print(f"Video with link {old_link} updated to {new_video['link']}")
