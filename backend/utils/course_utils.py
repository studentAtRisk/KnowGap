# Import necessary libraries
import asyncio
from openai import AsyncOpenAI
from config import Config
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def parse_date(date_str):
    
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(timezone.utc)  # Normalize to UTC
    return None


def clean_text(text):
    # Normalize and filter to keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)

async def get_quizzes(courseid, access_token, link):


    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes?per_page=100'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    unfiltered_data = await response.json()
                    max_date = datetime.now(timezone.utc)
                    # Sorts data by most recent unlocked quiz that is published to oldest

                    # Filter and sort the data
                    print(unfiltered_data)


                    data = sorted(
                        [
                            item for item in unfiltered_data
                            if item["published"] and item["all_dates"][0]["unlock_at"] and parse_date(item["all_dates"][0]["unlock_at"]) <= max_date
                        ],
                        key=lambda x: (
                            # Sort by unlock date in descending order (later dates first)
                            parse_date(x["all_dates"][0]["unlock_at"])
                        ),
                        reverse=True  # Sorting in descending order to get later dates first
                    )

                    
                    
                    quizlist = []
                    quizname = []
                    
                    for x in range(min(len(data), global_amtofquizzes)):
                        quizlist.append(data[x]["id"])
                        quizname.append(data[x]["title"])

                    print(quizname)
                    return quizlist, quizname 
                else:
                    print("did we error here?")
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        print(e)
        return {'error' : str(e)}, 500
