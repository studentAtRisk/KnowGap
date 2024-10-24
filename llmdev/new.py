# pip install --upgrade google-api-python-client
from googleapiclient.discovery import build
import configparser
import os
from pytube import extract

def get_video_details(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(part='statistics', id=video_id)
    response = request.execute()
    return response

def print_video_details(details):
    view_count = details['items'][0]['statistics']['viewCount']
    like_count = details['items'][0]['statistics']['likeCount']
    print(f'View count: {view_count}')
    print(f'Like count: {like_count}')
    print("Statistics: ", details['items'][0]['statistics'])


api_key = "AIzaSyB71CG_xbctso7Q7c_cRBfJJV1w5QHH-Y8"
print("api key: ", api_key)
video_id = '4sYPuSi8FVw'
details = get_video_details(video_id, api_key)
print_video_details(details)
