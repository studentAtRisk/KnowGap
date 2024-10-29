import os
import random
import asyncio
import aiohttp

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

async def get_youtube_videos(query, channel, max_results=5):
    search_query = f"{query} {channel}"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': search_query,
        'maxResults': max_results,
        'safeSearch': 'strict',
        'type': 'video',
        'key': YOUTUBE_API_KEY
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

youtube_queries = {
    'low': [
        "productivity tips for students",
        "how to stay motivated",
        "study hacks for better focus"
    ],
    'medium': [
        "school stress management",
        "exam stress relief",
        "how to handle academic pressure"
    ],
    'high': [
        "procrastination",
        "burnout",
        "student mental health help",
        "handling depression in college",
        "failing classes",
        "catch up in school"
    ]
}

mental_health_channels = {
    'low': ["Thomas Frank", "Ali Abdaal", "Psych2Go"],
    'medium': ["The School of Life", "Therapy in a Nutshell", "Dr. K"],
    'high': ['Psych2Go', "Psych Hub", "Dr. K"]
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

if __name__ == '__main__':
    async def main():
        risk_level = 'high'
        result_videos = await get_videos_for_risk_level(risk_level)
        random_video = get_random_video(result_videos)
        
        if random_video:
            print(f"Random Video Selected: Title: {random_video['title']}, Channel: {random_video['channelTitle']}, URL: {random_video['url']}")
        else:
            print("No videos found.")

    asyncio.run(main())
