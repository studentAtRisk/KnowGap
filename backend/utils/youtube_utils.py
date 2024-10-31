# utils/youtube_utils.py
from youtubesearchpython import VideosSearch
import re
from googleapiclient.discovery import build
from config import Config

async def fetch_video_for_topic(topic):
    """
    Fetch a single video for a given topic from YouTube.
    
    Parameters:
    - topic (str): The topic to search for.

    Returns:
    - dict: A dictionary containing video metadata (title, link, channel, thumbnail),
            or an empty dictionary if no video is found.
    """
    try:
        # Search for a single video related to the topic
        search = VideosSearch(topic, limit=1)
        search_results = search.result().get('result', [])

        if search_results:
            # Retrieve the first video in the search results
            video = search_results[0]
            video_data = {
                'title': video['title'],
                'link': video['link'],
                'channel': video['channel']['name'],
                'thumbnail': video['thumbnails'][0]['url']
            }
            return video_data

        # Return an empty dictionary if no results are found
        return {}

    except Exception as e:
        print(f"Error fetching videos for topic '{topic}': {e}")
        return {}

def extract_video_id(youtube_url):
    """Extracts the video ID from a YouTube URL."""
    video_id = None
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, youtube_url)
    if match:
        video_id = match.group(1)
    return video_id

def get_video_metadata(youtube_url):
    """Retrieves metadata for a YouTube video by URL."""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

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
