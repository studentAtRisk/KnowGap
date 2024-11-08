import os
import random
import asyncio
import aiohttp
from config import Config
from utils.youtube_utils import clean_metadata_text

# Define blacklisted terms for filtering video titles
BLACKLISTED_TERMS = ["adhd", "autism", "autistic", "disorder", "depression", "anxiety"]

async def get_youtube_videos(query, channel, max_results=5, retries=3):
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
    
    attempt = 0
    while attempt < retries:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = [
                        {
                            'title': clean_metadata_text(item['snippet']['title']),
                            'channelTitle': item['snippet']['channelTitle'],
                            'videoId': item['id']['videoId'],
                            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                        }
                        for item in data.get('items', [])
                        if '#shorts' not in item['snippet']['title'].lower()  # Filter out Shorts
                        and not any(term in item['snippet']['title'].lower() for term in BLACKLISTED_TERMS)  # Filter by blacklist
                    ]
                    
                    if videos:
                        return videos  # Return if we get valid videos
                    else:
                        print("Filtered out all videos (likely Shorts or blacklisted terms). Retrying...")
                else:
                    print(f"Error fetching videos: {response.status}")
                    
        attempt += 1
        await asyncio.sleep(1)  # Wait briefly before retrying

    # If no valid videos are found after retries
    print("No suitable videos found after retries.")
    return []

# Example lists for queries and channels
youtube_queries = {
    'low': [
        "finding internships and job opportunities",
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
        "How to bounce back after falling behind in classes",
        "avoiding burnout for students",
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
        "Dr. K",
        "Psychology with Dr. Ana"
        
    ],
    'medium': [
        "The School of Life",
        "TED-Ed",
        "Yale Well",
        "BrainCraft",
        "Dr. K",
        "Psychology with Dr. Ana"
    ],
    'high': [
        "It's Okay to be Smart",
        "Motivation2Study",
        "Study Vibes",
        "Success & Motivation",
        "Evan Carmichael",
        "Better Ideas",
        "UnJaded Jade",
        "Mike and Matty",
        "Psychology with Dr. Ana"
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
