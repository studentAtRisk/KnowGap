import os
from googleapiclient.discovery import build

# Set your API key here
API_KEY = 'YOUR_API_KEY'
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def youtube_search(query):
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=10
    ).execute()
    
    video_metadata_list = []
    
    for item in search_response.get('items', []):
        video_metadata = {
            'videoId': item['id']['videoId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channelTitle': item['snippet']['channelTitle'],
            'publishedAt': item['snippet']['publishedAt']
        }
        video_metadata_list.append(video_metadata)
    
    return video_metadata_list

if __name__ == '__main__':
    query = 'Python programming tutorials'
    
    results = youtube_search(query)
    
    for idx, video in enumerate(results):
        print(f"Result {idx + 1}:")
        print(f"Video ID: {video['videoId']}")
        print(f"Title: {video['title']}")
        print(f"Description: {video['description']}")
        print(f"Channel: {video['channelTitle']}")
        print(f"Published At: {video['publishedAt']}")
        print('-' * 50)
