# utils/youtube_utils.py
from youtubesearchpython import VideosSearch
import re
from googleapiclient.discovery import build
from config import Config
import aiohttp
import asyncio
import html
import logging

def clean_metadata_text(text: str) -> str:
    """
    Cleans up HTML-encoded characters in any metadata text, converting them to their intended form.
    
    Args:
        text (str): The text string potentially containing HTML entities.
    
    Returns:
        str: A cleaned-up version of the text.
    """
    return html.unescape(text)

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
        # Start the search
        logging.debug(f"Starting search for topic: {topic}")
        search = VideosSearch(topic, limit=1)
        
        # Fetch search results
        search_results = search.result()
        logging.debug(f"Raw search results for topic '{topic}': {search_results}")
        
        # Parse the search results
        results = search_results.get('result', [])
        
        if not results:
            logging.warning(f"No results found for topic '{topic}'")
            return {}

        # Extract video details from the first result
        video = results[0]  
        
        # Ensure video data contains expected keys
        video_data = {
            'title': clean_metadata_text(video.get('title', 'No Title Found')),
            'link': video.get('link', 'No Link Found'),
            'channel': video.get('channel', {}).get('name', 'No Channel Found'),
            'thumbnail': video.get('thumbnails', [{}])[0].get('url', 'No Thumbnail Found')
        }
        
        logging.debug(f"Extracted video data for topic '{topic}': {video_data}")
        return video_data

    except Exception as e:
        logging.error(f"Error fetching videos for topic '{topic}': {e}")
        return {}
    






def extract_video_id(youtube_url):
    """Extracts the video ID from a YouTube URL."""
    video_id = None
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, youtube_url)
    if match:
        video_id = match.group(1)
    return video_id


async def get_video_metadata(youtube_url):
    """Retrieves metadata for a YouTube video by URL asynchronously."""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    # YouTube API URL for getting video details
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={Config.YOUTUBE_API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                response_data = await response.json()

                if "items" in response_data and len(response_data["items"]) > 0:
                    video = response_data["items"][0]["snippet"]
                    metadata = {
                        "title": clean_metadata_text(video["title"]),
                        "link" : youtube_url,
                        "channel": video["channelTitle"],
                        "thumbnail": video["thumbnails"]["high"]["url"],
                    }
                    return metadata
                else:
                    return {"error": "Video not found"}
            else:
                return {"error": f"Failed to fetch metadata, status code: {response.status}"}