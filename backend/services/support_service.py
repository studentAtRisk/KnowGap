import os
import random
import asyncio
import aiohttp
from config import Config

async def get_youtube_videos(query, channel, max_results=5):
    search_query = f"{query} {channel}"
    url = Config.YOUTUBE_API_URL
    params = {
        'part': 'snippet',
        'q': search_query,
        'maxResults': max_results,
        'safeSearch': 'strict',
        'type': 'video',
        'key': Config.YOUTUBE_API_KEY
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                videos = [
                    {
                        'title': item['snippet']['title'],
                        'channelTitle': item['snippet']['channelTitle'],
                        'videoId': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    for item in data.get('items', [])
                ]
                return videos
            else:
                print(f"Error fetching videos: {response.status}")
                return []

youtube_queries =  {
    'low': [
        "time management tips for students",
        "how to stay organized in college",
        "healthy study habits",
        "boosting productivity for students",
        "balancing school and personal life"
    ],
    'medium': [
        "coping with school stress",
        "building resilience in college",
        "mindfulness practices for students",
        "healthy routines for academic success",
        "self-care tips for students"
    ],
    'high': [
        "overcoming procrastination",
        "avoiding burnout in college",
        "finding balance between studies and rest",
        "managing expectations in college",
        "self-compassion for students"
    ]
}

mental_health_channels = {
    'low': [
        "Thomas Frank",
        "Ali Abdaal",
        "Psych2Go",
        "StudyTee",
        "Amy Landino",
        "WellCast",
        "Lavendaire",
        "Dr. K"
    ],
    'medium': [
        "The School of Life",
        "TED-Ed",
        "Yale Well",
        "BrainCraft",
        "Dr. K"
    ],
    'high': [
        "It's Okay to be Smart",
        "Motivation2Study",
        "Study Vibes",
        "Success & Motivation",
        "Evan Carmichael",
        "Better Ideas",
        "UnJaded Jade",
        "Mike and Matty"
    ]
}

async def get_videos_for_risk_level(risk_level, max_results=3):
    query_list = youtube_queries.get(risk_level, [])
    channel_list = mental_health_channels.get(risk_level, [])
    
    if query_list and channel_list:
        query = random.choice(query_list)
        channel = random.choice(channel_list)
        videos = await get_youtube_videos(query, channel, max_results)
        return videos
    else:
        return []

def get_random_video(videos):
    if videos:
        return random.choice(videos)
    else:
        return None
