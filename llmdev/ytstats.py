import os
import math
import re
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from pytube import extract

class YTStatsUtility:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_video_statistics(self, link):
        youtube = build('youtube', 'v3', developerKey=self.api_key)
        try:
            request = youtube.videos().list(part='statistics', id=self.get_video_id(link))
            response = request.execute()
            return response['items'][0]['statistics']
        except Exception as e:
            print(f"Error fetching video statistics: {e}")
            return None

    def get_video_id(self, url):
        try:
            # try pytube first
            return extract.video_id(url)
        except Exception:
            print("Failed to extract video ID using pytube, falling back to regex")
            return self.get_video_id_fallback(url)

    def get_video_id_fallback(self, url):
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]

        # thank you stack overflow
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None


"""

if __name__ == "__main__":
    youtube_api_key = "AIzaSyB71CG_xbctso7Q7c_cRBfJJV1w5QHH-Y8"

    youtube_utils = YouTubeUtils(api_key=youtube_api_key)

    youtube_link = "https://www.youtube.com/watch?v=0oc49DyA3hU"

    video_id = youtube_utils.get_video_id(youtube_link)
    print(f"Video ID: {video_id}")

    if video_id:
        stats = youtube_utils.get_video_statistics(video_id)
        print("Video Statistics:", stats)
"""
