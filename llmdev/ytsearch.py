import json
from youtubesearchpython import VideosSearch

"""
query_videos: wrapper around ytsearch api that
returns the list of videos (default limit of 10) queried
by a search term
"""
def query_videos(query: str, num_results: int = 10):
    videos_search = VideosSearch(query, limit=num_results)
    video_results = videos_search.result()["result"]
    
    video_list = []
    for video in video_results:
        video_info = {
            "title": video["title"],
            "link": video["link"],
            "duration": video["duration"],
            "view_count": video["viewCount"]["short"],
            "published_time": video["publishedTime"],
            "channel_name": video["channel"]["name"]
        }
        video_list.append(video_info)
    
    return video_list
