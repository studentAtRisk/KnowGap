from googleapiclient.discovery import build
import re

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
        part="snippet",  # You can add 'contentDetails' or other parts if needed
        id=video_id
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video = response["items"][0]["snippet"]
        metadata = {
            "title": video["title"],
            "channel": video["channelTitle"],
            "thumbnail": video["thumbnails"]["high"]["url"],  # Use high-resolution thumbnail
            "description": video["description"]
        }
        return metadata
    else:
        return {"error": "Video not found"}

api_key = "YOUR_YOUTUBE_API_KEY"  # Replace with your actual YouTube Data API key
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with any YouTube link
video_metadata = get_video_metadata(youtube_url, api_key)

print(video_metadata)
